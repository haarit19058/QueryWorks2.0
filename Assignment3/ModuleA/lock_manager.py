# lock_manager.py
# Simple lock manager implementing Strict Two-Phase Locking (S2PL).
# Supports Shared (S) and Exclusive (X) locks keyed by (table_name, key).

import threading
import time
from collections import defaultdict

class LockTimeout(Exception):
    pass

class LockManager:
    def __init__(self):
        # locks: resource -> dict { 'mode': 'S'|'X', 'holders': set(tid), 'waiters': [ (tid, mode, event) ] }
        self._locks = {}
        self._global_lock = threading.Lock()

    def _resource_id(self, table_name, key):
        return f"{table_name}::{repr(key)}"

    def acquire(self, tid, table_name, key, mode="X", timeout=5.0):
        """
        Acquire lock for tid on resource (table_name, key).
        mode: 'S' or 'X'
        timeout: seconds to wait before raising LockTimeout
        """
        rid = self._resource_id(table_name, key)
        deadline = time.time() + timeout
        event = threading.Event()
        while True:
            with self._global_lock:
                entry = self._locks.get(rid)
                if entry is None:
                    # no lock, grant
                    self._locks[rid] = {"mode": mode, "holders": {tid}, "waiters": []}
                    return True
                else:
                    # existing lock
                    if entry["mode"] == "S" and mode == "S":
                        # shared requested and shared held -> add holder
                        entry["holders"].add(tid)
                        return True
                    elif entry["mode"] == "S" and mode == "X":
                        # upgrade to exclusive: only allowed if this tid is the only holder
                        if entry["holders"] == {tid}:
                            entry["mode"] = "X"
                            return True
                    elif entry["mode"] == "X":
                        # exclusive held
                        if entry["holders"] == {tid}:
                            # reentrant
                            return True
                # otherwise must wait
                entry = self._locks.setdefault(rid, {"mode": None, "holders": set(), "waiters": []})
                entry["waiters"].append((tid, mode, event))
            remaining = deadline - time.time()
            if remaining <= 0:
                # remove waiter
                with self._global_lock:
                    entry = self._locks.get(rid)
                    if entry:
                        entry["waiters"] = [w for w in entry["waiters"] if w[0] != tid]
                raise LockTimeout(f"Timeout acquiring lock {rid} for tid {tid}")
            event.wait(timeout=remaining)
            # loop and try again

    def release(self, tid, table_name, key):
        rid = self._resource_id(table_name, key)
        with self._global_lock:
            entry = self._locks.get(rid)
            if not entry:
                return
            if tid in entry["holders"]:
                entry["holders"].remove(tid)
            # if no holders, try to grant to waiters
            if not entry["holders"]:
                # pick next waiter(s)
                if not entry["waiters"]:
                    # remove lock entry
                    del self._locks[rid]
                else:
                    # grant to first waiter; if S-mode and subsequent waiters are S, grant them too
                    next_tid, next_mode, next_event = entry["waiters"].pop(0)
                    entry["mode"] = next_mode
                    entry["holders"].add(next_tid)
                    next_event.set()
                    if next_mode == "S":
                        # grant to other S waiters
                        s_waiters = [w for w in entry["waiters"] if w[1] == "S"]
                        for w in s_waiters:
                            entry["holders"].add(w[0])
                            w[2].set()
                        entry["waiters"] = [w for w in entry["waiters"] if w[1] != "S"]

    def release_all_for_tid(self, tid):
        """
        Release all locks held by tid.
        """
        with self._global_lock:
            to_release = []
            for rid, entry in list(self._locks.items()):
                if tid in entry["holders"]:
                    entry["holders"].remove(tid)
                    if not entry["holders"]:
                        to_release.append(rid)
            # notify waiters for released resources
            for rid in to_release:
                entry = self._locks.get(rid)
                if not entry:
                    continue
                if not entry["waiters"]:
                    del self._locks[rid]
                else:
                    next_tid, next_mode, next_event = entry["waiters"].pop(0)
                    entry["mode"] = next_mode
                    entry["holders"].add(next_tid)
                    next_event.set()
                    if next_mode == "S":
                        s_waiters = [w for w in entry["waiters"] if w[1] == "S"]
                        for w in s_waiters:
                            entry["holders"].add(w[0])
                            w[2].set()
                        entry["waiters"] = [w for w in entry["waiters"] if w[1] != "S"]