import pandas as pd
from bplustree import BPlusTree

class Table:
    """
    Represents a database table.
    Stores rows as a dictionary: {primary_key: row_data}
    Transaction-aware: insert/update/delete can be executed under a transaction id (tid).
    """

    def __init__(self, name, key_column, schema=None):
        self.name = name
        self.key_column = key_column
        self.schema = schema or {}
        self.rows = {}
        self.index = BPlusTree(order=4)

    def validate_record(self, record):
        for col, dtype in self.schema.items():
            if col not in record:
                return False, f"Missing column {col}"
            try:
                val = record[col]
                if dtype == int and isinstance(val, int) and val < 0:
                    return False, f"Invalid negative value for {col}"
                if not isinstance(val, dtype):
                    return False, f"Wrong type for {col}: expected {dtype}, got {type(val)}"
            except Exception as e:
                return False, str(e)
        return True, None

    def load_csv(self, path):
        """Load data from CSV into table."""
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            key = row[self.key_column]
            self.rows[key] = row.to_dict()

    # -----------------------
    # Transaction-aware methods
    # -----------------------
    def insert(self, row, tid=None, dbm=None):
        key = row[self.key_column]
        if tid and dbm:
            dbm.txn_acquire_lock(tid, self.name, key, mode="X")
            dbm.txn_log_op(tid, self.name, key, "INSERT", None, row)
        self.rows[key] = row
        self.index.insert(key, row)

    def delete(self, key, tid=None, dbm=None):
        if key in self.rows:
            old_row = self.rows[key]
            if tid and dbm:
                dbm.txn_acquire_lock(tid, self.name, key, mode="X")
                dbm.txn_log_op(tid, self.name, key, "DELETE", old_row, None)
            del self.rows[key]
            self.index.delete(key)

    def update(self, key, new_row, tid=None, dbm=None):
        if key in self.rows:
            old_row = self.rows[key]
            if tid and dbm:
                dbm.txn_acquire_lock(tid, self.name, key, mode="X")
                dbm.txn_log_op(tid, self.name, key, "UPDATE", old_row, new_row)
            self.rows[key] = new_row
            self.index.update(key, new_row)
            return True
        return False

    def get(self, key):
        """Retrieve row by key."""
        return self.rows.get(key)

    def range_query(self, start_key, end_key):
        """Return all rows whose key is between start_key and end_key (inclusive)."""
        return {k: v for k, v in self.rows.items() if start_key <= k <= end_key}

    def get_all(self):
        """Return all rows sorted by primary key."""
        return [(k, self.rows[k]) for k in sorted(self.rows)]

    # -----------------------
    # Recovery helpers
    # -----------------------
    def _apply_redo_insert(self, key, new_row):
        self.rows[key] = new_row

    def _apply_redo_update(self, key, new_row):
        self.rows[key] = new_row

    def _apply_redo_delete(self, key):
        if key in self.rows:
            del self.rows[key]

    def _apply_undo_insert(self, key, old_row):
        # undo of delete -> insert old_row
        if old_row is not None:
            self.rows[key] = old_row

    def _apply_undo_update(self, key, old_row):
        if old_row is not None:
            self.rows[key] = old_row
        else:
            if key in self.rows:
                del self.rows[key]

    def _apply_undo_delete(self, key):
        # undo of insert -> delete
        if key in self.rows:
            del self.rows[key]