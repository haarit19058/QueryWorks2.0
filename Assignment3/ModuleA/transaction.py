# transaction.py
# Transaction manager that coordinates WAL, locks, and transaction lifecycle.

import threading
import time
from wal import WAL
from lock_manager import LockManager
import os

class TransactionError(Exception):
    pass

class TransactionManager:
    def __init__(self, db_path, pager_apply_callback=None):
        """
        db_path: directory where WAL and checkpoint are stored
        pager_apply_callback: optional function to apply a WAL OP to the storage layer:
            pager_apply_callback(op_record) -> None
        """
        self.wal = WAL(db_path)
        self.lockmgr = LockManager()
        self._tid_counter = 0
        self._tid_lock = threading.Lock()
        self._active = {}  # tid -> {'start_lsn': int, 'locks': set((table,key))}
        self._pager_apply = pager_apply_callback
        self.db_path = db_path
        self.pager_apply_callback = pager_apply_callback
        self.log_path = os.path.join(self.db_path, "wal.log")  # <-- add this
        # open/create WAL file if needed
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w") as f:
                f.write("")

    def _next_tid(self):
        with self._tid_lock:
            self._tid_counter += 1
            return f"T{int(time.time()*1000)}_{self._tid_counter}"

    def begin(self):
        tid = self._next_tid()
        rec = {"type": "BEGIN", "tid": tid, "payload": {}}
        lsn = self.wal.append(rec)
        self.wal.flush()
        self._active[tid] = {"start_lsn": lsn, "locks": set()}
        return tid

    def acquire_lock(self, tid, table, key, mode="X", timeout=5.0):
        self.lockmgr.acquire(tid, table, key, mode=mode, timeout=timeout)
        self._active.setdefault(tid, {"start_lsn": None, "locks": set()})
        self._active[tid]["locks"].add((table, key))

    def log_op(self, tid, table, key, op_type, old_value, new_value):
        """
        Log an operation for tid. This writes an OP record to WAL but does not flush.
        Caller must ensure write-ahead rule: flush WAL before applying to storage.
        """
        rec = {
            "type": "OP",
            "tid": tid,
            "payload": {
                "table": table,
                "key": key,
                "op": op_type,  # 'INSERT'|'UPDATE'|'DELETE'
                "old": old_value,
                "new": new_value,
            },
        }
        lsn = self.wal.append(rec)
        return lsn

    def commit(self, tid):
        """
        Commit transaction: write COMMIT record, flush WAL, then release locks.
        """
        if tid not in self._active:
            raise TransactionError("Unknown transaction")
        rec = {"type": "COMMIT", "tid": tid, "payload": {}}
        self.wal.append(rec)
        # flush WAL to ensure durability of commit
        self.wal.flush()
        # release locks after commit (strict 2PL: locks held until commit)
        self.lockmgr.release_all_for_tid(tid)
        # remove from active
        del self._active[tid]

    def abort(self, tid):
        """
        Abort transaction: write ABORT record, flush WAL, then undo operations if possible,
        and release locks.
        """
        if tid not in self._active:
            return
        rec = {"type": "ABORT", "tid": tid, "payload": {}}
        self.wal.append(rec)
        self.wal.flush()
        # Undo: scan WAL backwards for this tid and apply old images via pager_apply
        if self._pager_apply:
            # read all WAL and find OPs for this tid
            all_recs = list(self.wal.read_all())
            for rec in reversed(all_recs):
                if rec.get("tid") == tid and rec.get("type") == "OP":
                    payload = rec["payload"]
                    undo_rec = {
                        "type": "UNDO_OP",
                        "tid": tid,
                        "payload": payload
                    }
                    try:
                        self._pager_apply(undo_rec)
                    except Exception:
                        # best-effort; continue
                        pass
        # release locks
        self.lockmgr.release_all_for_tid(tid)
        del self._active[tid]

    def close(self):
        try:
            self.wal.close()
        except Exception:
            pass
        
    def reset_log(self):
        """Clear the WAL/log file after checkpoint."""
        try:
            with open(self.log_path, "w") as f:
                f.write("")  # truncate
            print("[Checkpoint] WAL log reset.")
        except Exception as e:
            print("Error resetting log:", e)
