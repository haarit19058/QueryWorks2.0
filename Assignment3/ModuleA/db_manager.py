from table import Table
from bplustree import BPlusTree
from transaction import TransactionManager
from recovery import RecoveryManager
import os
import pickle


class DatabaseManager:
    """
    Manages tables and their corresponding B+ Tree indexes.
    Acts as the interface between storage (Table) and indexing (B+ Tree).
    Integrates a TransactionManager and RecoveryManager to provide ACID support.
    """

    def __init__(self, db_path=None):
        """
        db_path: optional directory where WAL/checkpoint files will be stored.
                 If None, uses current working directory.
        """
        # core structures (existing)
        self.tables = {}
        self.indexes = {}
        self.db_name = None

        # transaction/recovery integration
        self.db_path = db_path or os.getcwd()
        # TransactionManager and RecoveryManager are created here.
        # pager_apply_callback is set to a bound method that dispatches REDO/UNDO to tables.
        self._txn_mgr = TransactionManager(self.db_path, pager_apply_callback=self._pager_apply_callback)
        self._recovery_mgr = RecoveryManager(self.db_path, pager_apply_callback=self._pager_apply_callback)

        # Flag to ensure we run recovery once after at least one table exists.
        # We will attempt recovery after the first table is created (see create_table).
        self._recovered = False
        
        self._txn_count = 0  # track number of committed transactions for checkpointing

    # -----------------------
    # Pager apply callback
    # -----------------------
    def _pager_apply_callback(self, wal_record):
        """
        Called by TransactionManager.abort() and RecoveryManager.recover()
        wal_record: dict with keys 'type' ('REDO_OP'|'UNDO_OP') and 'payload'
        payload: { 'table': table_name, 'key': key, 'op': 'INSERT'|'UPDATE'|'DELETE', 'old': ..., 'new': ... }
        This method dispatches the REDO/UNDO to the appropriate Table object.
        """
        if not wal_record:
            return
        typ = wal_record.get("type")
        payload = wal_record.get("payload", {})
        table_name = payload.get("table")
        key = payload.get("key")
        op = payload.get("op")
        old = payload.get("old")
        new = payload.get("new")

        # Lookup table object from this manager's registry
        tbl = self.get_table(table_name)
        if tbl is None:
            # If table not present, skip (best-effort). Recovery will be attempted again
            # when tables are created (we run recovery after first create_table).
            return

        # Dispatch to table-level recovery helpers if available, otherwise use public API.
        if typ == "REDO_OP":
            if op == "INSERT":
                try:
                    tbl._apply_redo_insert(key, new)
                except AttributeError:
                    tbl.insert({tbl.key_column: key, **(new if isinstance(new, dict) else {})})
            elif op == "UPDATE":
                try:
                    tbl._apply_redo_update(key, new)
                except AttributeError:
                    tbl.update(key, new)
            elif op == "DELETE":
                try:
                    tbl._apply_redo_delete(key)
                except AttributeError:
                    try:
                        tbl.delete(key)
                    except Exception:
                        pass
        elif typ == "UNDO_OP":
            if op == "INSERT":
                # undo of insert -> delete
                try:
                    tbl._apply_undo_delete(key)
                except AttributeError:
                    try:
                        tbl.delete(key)
                    except Exception:
                        pass
            elif op == "UPDATE":
                try:
                    tbl._apply_undo_update(key, old)
                except AttributeError:
                    try:
                        tbl.update(key, old)
                    except Exception:
                        # if update fails, try insert old
                        try:
                            tbl.insert({tbl.key_column: key, **(old if isinstance(old, dict) else {})})
                        except Exception:
                            pass
            elif op == "DELETE":
                # undo of delete -> insert old
                try:
                    tbl._apply_undo_insert(key, old)
                except AttributeError:
                    try:
                        tbl.insert({tbl.key_column: key, **(old if isinstance(old, dict) else {})})
                    except Exception:
                        pass

    # -----------------------
    # Transaction API wrappers
    # -----------------------
    def txn_begin(self):
        """Start a new transaction and return its transaction id (tid)."""
        return self._txn_mgr.begin()

    def txn_acquire_lock(self, tid, table, key, mode="X", timeout=5.0):
        """Acquire a lock for a transaction on (table, key)."""
        return self._txn_mgr.acquire_lock(tid, table, key, mode=mode, timeout=timeout)

    def txn_log_op(self, tid, table, key, op_type, old_value, new_value):
        """Log an operation for the given transaction (does not flush)."""
        return self._txn_mgr.log_op(tid, table, key, op_type, old_value, new_value)

    def txn_commit(self, tid):
        """Commit the transaction (writes COMMIT to WAL and fsyncs)."""
        result = self._txn_mgr.commit(tid)

        # After commit, persist all indexes to disk
        for table_name in self.tables.keys():
            self.save_index(table_name)

        # Increment transaction counter
        self._txn_count += 1
        if self._txn_count >= 10:
            self.checkpoint()
            self._txn_count = 0

        return result

    def txn_abort(self, tid):
        """Abort the transaction (writes ABORT to WAL, attempts undo, releases locks)."""
        return self._txn_mgr.abort(tid)

    # -----------------------
    # Existing API methods (unchanged behavior, with recovery hook)
    # -----------------------
    def create_database(self, db_name):
        """
        Register a named database.
        """
        self.db_name = db_name

    def list_databases(self):
        """
        Return the list of registered databases.
        """
        return [self.db_name] if self.db_name else []

    def delete_database(self):
        """
        Drop all tables and reset the database.
        """
        self.tables.clear()
        self.indexes.clear()
        self.db_name = None

    def create_table(self, name, key, schema=None, order=5):
        table = Table(name, key, schema=schema)
        self.tables[name] = table

        # Try to load persisted index, otherwise create new
        self.indexes[name] = BPlusTree(order=order)
        self.load_index(name)

        # Recovery hook
        if not self._recovered:
            try:
                self._recovery_mgr.recover()
            except Exception:
                pass
            self._recovered = True

        return table

    def list_tables(self):
        """
        Return all table names in the database.
        """
        return list(self.tables.keys())

    def get_table(self, table_name):
        """
        Retrieve the Table object for a given table name.
        """
        return self.tables.get(table_name)

    def delete_table(self, table_name):
        """
        Drop a table and its index.
        """
        if table_name in self.tables:
            del self.tables[table_name]
            del self.indexes[table_name]
            return True

        return False

    def build_index(self, table_name):
        """
        Build index from existing table data.
        """
        table = self.tables[table_name]
        tree = self.indexes[table_name]

        # Insert all rows into B+ Tree
        for key, row in table.rows.items():
            tree.insert(key, row)

    def search(self, table_name, key):
        """
        Search using B+ Tree index.
        """
        tree = self.indexes[table_name]

        return tree.search(key)

    def insert(self, table_name, row):
        """
        Insert into both table and index.
        NOTE: This method remains a convenience wrapper. For ACID transactions,
        use txn_begin/txn_log_op/txn_commit and call Table.insert with tid.
        """
        table = self.tables[table_name]
        tree = self.indexes[table_name]
        key = row[table.key_column]

        # Insert into table
        table.insert(row)

        # Insert into B+ Tree index
        tree.insert(key, row)

    def delete(self, table_name, key):
        """
        Delete from both table and index.
        NOTE: For transactional deletes, use txn_begin/txn_log_op/txn_commit and call Table.delete with tid.
        """
        table = self.tables[table_name]
        tree = self.indexes[table_name]

        table.delete(key)
        tree.delete(key)

    def range_query(self, table_name, start, end):
        """
        Perform range query using B+ Tree.
        """
        tree = self.indexes[table_name]

        return tree.range_query(start, end)

    def update(self, table_name, key, new_row):
        """
        Update record in both the table and the B+ Tree index.
        Returns True if the key existed and was updated, False otherwise.
        NOTE: For transactional updates, use txn_begin/txn_log_op/txn_commit and call Table.update with tid.
        """
        table = self.tables[table_name]
        tree = self.indexes[table_name]
        result = tree.update(key, new_row)

        if result:
            table.rows[key] = new_row

        return result

    def checkpoint(self):
        """
        Flush current state of all tables and indexes to disk,
        and refresh the WAL/log.
        """
        print("[Checkpoint] Saving all tables and refreshing log...")
        for table_name in self.tables.keys():
            self.save_index(table_name)
        # Reset WAL/log file
        self._txn_mgr.reset_log()
    
    # -----------------------
    # Persistence helpers
    # -----------------------
    def _index_filepath(self, table_name):
        """Return the file path for persisting a table's B+ tree index."""
        return os.path.join(self.db_path, f"{self.db_name}_{table_name}_bplustree.pkl")

    def save_index(self, table_name):
        """Save the B+ tree index of a table to disk."""
        tree = self.indexes.get(table_name)
        if tree:
            filepath = self._index_filepath(table_name)
            with open(filepath, "wb") as f:
                pickle.dump(tree, f)

    def load_index(self, table_name):
        """Load the B+ tree index of a table from disk, if available."""
        filepath = self._index_filepath(table_name)
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                self.indexes[table_name] = pickle.load(f)