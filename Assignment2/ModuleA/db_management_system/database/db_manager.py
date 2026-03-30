"""
Database Manager Module.

This class serves as the primary orchestrator for the storage engine. 
It bridges the in-memory 'Table' representations with their persistent, 
on-disk 'BPlusTree' indexes, ensuring that data remains synchronized 
across both systems and safely handling data-type serialization.
"""

from .table import Table
from .bplustree import BPlusTree
from .serializer import StrSerializer

class DatabaseManager:
    """
    Coordinates CRUD operations across tables and their corresponding B+ Tree indexes.
    Enforces string-based primary keys to guarantee stable binary serialization.
    """
    
    def __init__(self):
        # Maps table names to their in-memory Table objects
        self.tables = {}
        # Maps table names to their persistent BPlusTree instances
        self.indexes = {}
        self.db_name = None
        
    def create_database(self, db_name):
        """Initializes the active database context."""
        self.db_name = db_name

    def list_databases(self):
        """Returns a list containing the currently active database, if any."""
        return [self.db_name] if self.db_name else []

    def delete_database(self):
        """Purges the current database context, clearing all loaded tables and indexes."""
        self.tables.clear()
        self.indexes.clear()
        self.db_name = None

    def create_table(self, name, key, schema=None, order=5):
        """
        Registers a new table and provisions a dedicated persistent B+ Tree file.
        
        Args:
            name (str): The name of the table (used for file generation).
            key (str): The column designated as the Primary Key.
            schema (dict): Mapping of column names to their data types.
            order (int): The branching factor for the B+ Tree.
        """
        # 1. Initialize the logical table
        table = Table(name, key, schema=schema)   
        self.tables[name] = table
        
        # 2. Provision a physically isolated file for this table's index
        target_filename = f'./{name}.db'
        
        # 3. Initialize the tree with a StrSerializer and a generous key capacity 
        #    to prevent serialization crashes on large IDs or UUIDs.
        self.indexes[name] = BPlusTree(
            filename=target_filename, 
            order=order,
            key_size=128, 
            serializer=StrSerializer()
        ) 
        
        return table

    def list_tables(self):
        """Retrieves the names of all currently registered tables."""
        return list(self.tables.keys())

    def get_table(self, table_name):
        """Fetches the logical Table object by its name."""
        return self.tables.get(table_name)

    def delete_table(self, table_name):
        """Removes a table and unloads its corresponding index."""
        if table_name in self.tables:
            del self.tables[table_name]
            del self.indexes[table_name]
            return True
        return False

    def build_index(self, table_name):
        """
        Synchronizes an empty B+ Tree with pre-existing table data.
        Forces all keys to strings to maintain serialization safety.
        """
        table = self.tables[table_name]
        tree = self.indexes[table_name]

        # Bulk load all rows into the persistent tree
        for key, row in table.rows.items():
            tree.insert(str(key), row)

    def insert(self, table_name, row):
        """
        Commits a new record to both the in-memory table and the persistent index.
        """
        table = self.tables[table_name]
        tree = self.indexes[table_name]
        
        # Isolate the primary key and cast it to a string for the serializer
        pk_value = str(row[table.key_column])

        # Commit to memory
        table.insert(row)

        # Commit to disk via B+ Tree
        tree.insert(pk_value, row)
        
    def search(self, table_name, key):
        """
        Queries the persistent B+ Tree index for a specific record.
        """
        tree = self.indexes[table_name]
        
        # Cast the search query to a string to match stored data format
        return tree.search(str(key))

    def delete(self, table_name, key):
        """
        Purges a record simultaneously from the in-memory table and the disk index.
        """
        table = self.tables[table_name]
        tree = self.indexes[table_name]

        # Cast to string to ensure the engine targets the correct binary footprint
        string_key = str(key)

        table.delete(string_key)
        tree.delete(string_key)

    def range_query(self, table_name, start, end):
        """
        Executes a lexicographical range scan across the B+ Tree leaves.
        """
        tree = self.indexes[table_name]
        
        # Cast bounds to strings. (Note: Ensure bplustree.py handles the inclusive 
        # string bound logic we discussed previously).
        return tree.range_query(str(start), str(end))
    
    def update(self, table_name, key, new_row):
        """
        Overwrites an existing record in both storage locations.
        Returns True if the record was successfully updated, False if it did not exist.
        """
        table = self.tables[table_name]
        tree = self.indexes[table_name]
        
        string_key = str(key)
        
        # Execute update on disk first
        is_successful = tree.update(string_key, new_row)
        
        # If disk update succeeds, synchronize the memory layer
        if is_successful:   
            table.rows[string_key] = new_row
        
        return is_successful