# recovery.py
# Recovery logic: redo committed transactions and undo uncommitted ones.

import json
from wal import WAL

class RecoveryManager:
    def __init__(self, db_path, pager_apply_callback):
        """
        pager_apply_callback(record): function that applies an OP/UNDO_OP to the storage layer.
        record is a WAL record dict.
        """
        self.wal = WAL(db_path)
        self._apply = pager_apply_callback

    def recover(self):
        """
        Perform recovery:
          1. Read WAL
          2. Identify committed transactions
          3. Redo all OPs for committed transactions in LSN order
          4. Undo OPs for uncommitted transactions (in reverse LSN order)
        """
        records = list(self.wal.read_all())
        committed = set()
        tids_with_ops = {}
        for rec in records:
            t = rec.get("tid")
            if rec.get("type") == "COMMIT":
                committed.add(t)
            if rec.get("type") == "OP":
                tids_with_ops.setdefault(t, []).append(rec)

        # REDO phase: apply all OPs for committed transactions in order
        for rec in records:
            if rec.get("type") == "OP" and rec.get("tid") in committed:
                try:
                    self._apply({"type": "REDO_OP", "tid": rec.get("tid"), "payload": rec.get("payload")})
                except Exception:
                    # best-effort; continue
                    pass

        # UNDO phase: for transactions that are not committed, undo their ops in reverse order
        uncommitted = [t for t in tids_with_ops.keys() if t not in committed]
        for t in uncommitted:
            ops = tids_with_ops.get(t, [])
            for rec in reversed(ops):
                try:
                    self._apply({"type": "UNDO_OP", "tid": t, "payload": rec.get("payload")})
                except Exception:
                    pass

        # Optionally, write a checkpoint after recovery (caller can call wal.checkpoint)
        return True