"""
Database Manager Module.

This class serves as the primary orchestrator for the storage engine. 
It bridges the in-memory 'Table' representations with their persistent, 
on-disk 'BPlusTree' indexes, ensuring that data remains synchronized 
across both systems and safely handling data-type serialization.
"""

from .table import Table


class DatabaseManager:
    """
    Coordinates CRUD operations across tables.
    Each table intrinsically manages its own persistent B+ Tree instance.
    """
    
    def __init__(self):
        # Maps table names to their in-memory Table objects which handle the tree
        self.tables = {}
        self.db_name = None
        
    def create_database(self, db_name):
        """Initializes the active database context."""
        self.db_name = db_name

    def list_databases(self):
        """Returns a list containing the currently active database, if any."""
        return [self.db_name] if self.db_name else []

    def delete_database(self):
        """Purges the current database context, clearing all loaded tables."""
        for name, table in self.tables.items():
            if hasattr(table.tree, 'close'):
               table.tree.close()
        self.tables.clear()
        self.db_name = None

    def create_table(self, name, key, schema=None, order=5):
        """
        Registers a new table.
        The persistent B+ Tree file is provisioned directly within the Table class.
        """
        # Initialize the logical table which manages its own B+ tree index
        table = Table(name, key, schema=schema, order=order)   
        self.tables[name] = table
        return table

    def list_tables(self):
        """Retrieves the names of all currently registered tables."""
        return list(self.tables.keys())

    def get_table(self, table_name):
        """Fetches the Table abstraction by its name."""
        return self.tables.get(table_name)

    def delete_table(self, table_name):
        """Removes a table and unloads its corresponding index."""
        if table_name in self.tables:
            table = self.tables.pop(table_name)
            if hasattr(table.tree, 'close'):
                table.tree.close()
            return True
        return False

    def join(self, left_table_name, right_table_name, left_col, right_col):
        """
        Performs an Inner Join between two tables.
        Leverages B+ Tree indexes on the right table for O(N * log M) performance.
        """
        left_table = self.get_table(left_table_name)
        right_table = self.get_table(right_table_name)
        
        if not left_table or not right_table:
            raise ValueError("Both tables must exist to perform a join.")
            
        joined_results = []
        
        # 1. Get all rows from the Left Table (Full Scan on Left)
        left_rows = left_table.get_all() 
        
        for pk, left_row in left_rows:
            join_val = left_row.get(left_col)
            if join_val is None:
                continue
                
            # 2. Probe the Right Table using our B+ Tree Indexes!
            # Scenario A: The join column is the Right Table's Primary Key
            if right_col == right_table.key_column:
                right_row = right_table.search(join_val)
                if right_row:
                    joined_results.append({**left_row, **right_row})
                    
            # Scenario B: The join column has a Secondary Index
            elif right_col in right_table.secondary_indexes:
                matching_rows = right_table.search_by(right_col, join_val)
                for right_row in matching_rows:
                    joined_results.append({**left_row, **right_row})
                    
            # Scenario C: No index exists! Fallback to slow Nested Loop Join
            else:
                raise ValueError(f"For performance, {right_table_name}.{right_col} must be indexed to perform a join!")
                
        return joined_results

    def __getattr__(self, name):
        """Allows MongoDB-like dot notation access: db.table_name.insert(...)"""
        if name in self.tables:
            return self.tables[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'. "
                             f"Ensure table '{name}' exists.")

    def __getitem__(self, name):
        """Allows dictionary-style notation access: db['table_name'].insert(...)"""
        if name in self.tables:
            return self.tables[name]
        raise KeyError(f"Table '{name}' does not exist.")