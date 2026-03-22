from .table import Table
from .bplustree import BPlusTree


class DatabaseManager:
    """
    Manages tables and their corresponding B+ Tree indexes.
    Acts as the interface between storage (Table) and indexing (B+ Tree).
    """
    
    def __init__(self):

        self.tables = {}
        self.indexes = {}
        self.db_name = None
     
        
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
        """
        Create a new table and initialize its B+ Tree index.
        schema: dict of {column_name: data_type}
        order:  B+ Tree branching factor (default 5)
        """
        table = Table(name, key, schema=schema)   
        self.tables[name]  = table
        self.indexes[name] = BPlusTree(order=order) 
        
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
        """
        table = self.tables[table_name]
        tree = self.indexes[table_name]
        result = tree.update(key, new_row)
        
        if result:   
            table.rows[key] = new_row
        
        return result