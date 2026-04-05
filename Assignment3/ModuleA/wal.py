# wal.py
# Write-Ahead Log manager for multi-table transactions.
# Provides append, flush, read (for recovery), and checkpointing.

import os
import json
import threading
import time

WAL_FILENAME = "db_wal.log"
CHECKPOINT_FILENAME = "db_wal.checkpoint"

class WAL:
    """
    Simple append-only WAL with JSON records, each record on its own line.
    Each record is a dict with at least:
      - lsn: integer log sequence number
      - type: 'BEGIN' | 'OP' | 'COMMIT' | 'ABORT' | 'CHECKPOINT'
      - tid: transaction id (for BEGIN/OP/COMMIT/ABORT)
      - payload: operation-specific dict
    """

    def __init__(self, path):
        self.path = os.path.join(path, WAL_FILENAME)
        self.lock = threading.Lock()
        self._ensure_file()
        self._lsn = self._recover_last_lsn()
        self._file = open(self.path, "a+b", buffering=0)  # unbuffered binary append

    def _ensure_file(self):
        d = os.path.dirname(self.path)
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        if not os.path.exists(self.path):
            open(self.path, "wb").close()

    def _recover_last_lsn(self):
        # Read file to find last LSN
        try:
            with open(self.path, "rb") as f:
                last = 0
                for line in f:
                    try:
                        rec = json.loads(line.decode("utf-8"))
                        last = max(last, rec.get("lsn", 0))
                    except Exception:
                        continue
                return last
        except FileNotFoundError:
            return 0

    def append(self, record):
        """
        Append a record (dict). WAL will assign LSN if not present.
        Returns assigned lsn.
        """
        with self.lock:
            if "lsn" not in record:
                self._lsn += 1
                record["lsn"] = self._lsn
            line = (json.dumps(record) + "\n").encode("utf-8")
            self._file.write(line)
            return record["lsn"]

    def flush(self):
        """
        Ensure WAL is durable on disk (fsync).
        """
        with self.lock:
            try:
                self._file.flush()
                os.fsync(self._file.fileno())
            except Exception:
                # best-effort; caller should handle failures
                raise

    def close(self):
        with self.lock:
            try:
                self._file.flush()
                os.fsync(self._file.fileno())
            except Exception:
                pass
            try:
                self._file.close()
            except Exception:
                pass

    def iterate_from(self, start_lsn=1):
        """
        Generator that yields records from WAL starting at start_lsn.
        """
        with open(self.path, "rb") as f:
            for line in f:
                try:
                    rec = json.loads(line.decode("utf-8"))
                except Exception:
                    continue
                if rec.get("lsn", 0) >= start_lsn:
                    yield rec

    def read_all(self):
        return list(self.iterate_from(1))

    def checkpoint(self, active_tids):
        """
        Write a checkpoint record listing active transactions and last lsn.
        """
        rec = {
            "type": "CHECKPOINT",
            "tid": None,
            "payload": {"active_tids": list(active_tids)},
        }
        lsn = self.append(rec)
        self.flush()
        # also write a small checkpoint file for quick startup
        cp_path = os.path.join(os.path.dirname(self.path), CHECKPOINT_FILENAME)
        try:
            with open(cp_path, "w", encoding="utf-8") as fh:
                json.dump({"last_lsn": lsn, "active_tids": list(active_tids)}, fh)
                fh.flush()
                os.fsync(fh.fileno())
        except Exception:
            pass
        return lsn