import pandas as pd
from .bplustree import BPlusTree
from .serializer import StrSerializer

class Table:
    """
    Represents a database table.
    Stores rows directly into a persistent BPlusTree index.
    """
    
    def __init__(self, name, key_column, schema=None, order=5):
        self.name       = name
        self.key_column = key_column
        self.schema     = schema or {}  
        self.order      = order
        self.secondary_indexes = {}
        
        target_filename = f'./{self.name}.table'
        self.tree = BPlusTree(
            filename=target_filename, 
            order=order,
            key_size=128, 
            serializer=StrSerializer()
        )
  
    def create_index(self, column_name):
        """
        Creates a secondary B+ Tree index on the specified column.
        Keys are the column values, and values are lists of primary keys.
        """
        if self.schema and column_name not in self.schema:
            raise ValueError(f"Column '{column_name}' not found in schema.")
            
        index_filename = f'./{self.name}_{column_name}_idx.db'
        
        self.secondary_indexes[column_name] = BPlusTree(
            filename=index_filename, 
            order=self.order,
            key_size=128, 
            serializer=StrSerializer()
        )
        
    def validate_record(self, record):
        """
        Validate a record against the table schema.
        Returns (True, None) on success, (False, error_msg) on failure.
        Skips validation if no schema was defined.
        """
        if not self.schema:
            return True, None

        for col, dtype in self.schema.items():
            if col not in record:
                return False, f"Missing required column: '{col}'"
            
            val = record[col]
            
            if val is not None and not isinstance(val, dtype):
                try:
                    dtype(val)
                except (ValueError, TypeError):
                    return False, (
                        f"Column '{col}' expects {dtype.__name__}, "
                        f"got {type(val).__name__}"
                    )
        
        return True, None


    def load_csv(self, path):
        """
        Load data from CSV into table persistent index.
        Each row is stored using key_column as key.
        """
        df = pd.read_csv(path)

        for _, row in df.iterrows():
            key = str(row[self.key_column])
            self.insert(row.to_dict())


    def insert(self, row):
        """
        Insert a row into the primary tree and update any secondary indexes.
        """
        pk = str(row[self.key_column])
        
        # 1. Update secondary indexes First
        for col, idx in self.secondary_indexes.items():
            if col in row:
                sec_key = str(row[col])
                # Secondary indices store a list of primary keys
                existing_pks = idx.search(sec_key) or []
                if pk not in existing_pks:
                    existing_pks.append(pk)
                    if idx.search(sec_key) is not None:
                        idx.update(sec_key, existing_pks)
                    else:
                        idx.insert(sec_key, existing_pks)
        
        # 2. Insert into Primary Tree
        self.tree.insert(pk, row)


    def delete(self, key):
        """
        Delete row by primary key from primary tree and clean up secondary indexes.
        """
        pk = str(key)
        # Fetch the row first so we know which secondary keys to remove
        row = self.tree.search(pk)
        if not row:
            return  # Nothing to delete
            
        # Clean up secondary indexes
        for col, idx in self.secondary_indexes.items():
            if col in row:
                sec_key = str(row[col])
                existing_pks = idx.search(sec_key)
                if existing_pks and pk in existing_pks:
                    existing_pks.remove(pk)
                    if not existing_pks: # If empty, remove the key completely
                        idx.delete(sec_key)
                    else:
                        idx.update(sec_key, existing_pks)

        self.tree.delete(pk)


    def search(self, key):
        """
        Retrieve row by primary key.
        """
        return self.tree.search(str(key))


    def search_by(self, column_name, value):
        """
        Retrieve rows using a secondary index.
        """
        if column_name not in self.secondary_indexes:
            raise ValueError(f"No secondary index exists for column '{column_name}'")
            
        pks = self.secondary_indexes[column_name].search(str(value))
        if not pks:
            return []
            
        # Fetch actual records from primary tree
        results = []
        for pk in pks:
            row = self.tree.search(pk)
            if row:
                results.append(row)
        return results


    def get(self, key):
        """
        Retrieve row by primary key.
        """
        return self.search(key)
    
    
    def update(self, key, new_row):
        """
        Update a row by primary key and synchronize all secondary indexes. Returns True if found.
        """
        pk = str(key)
        old_row = self.tree.search(pk)
        
        if not old_row:
            return False
            
        # Synchronize secondary indexes for columns whose values changed
        for col, idx in self.secondary_indexes.items():
            old_val = str(old_row[col]) if col in old_row else None
            new_val = str(new_row[col]) if col in new_row else None
            
            if old_val != new_val:
                # 1. Remove from old secondary key list
                if old_val is not None:
                    old_pks = idx.search(old_val)
                    if old_pks and pk in old_pks:
                        old_pks.remove(pk)
                        if not old_pks:
                            idx.delete(old_val)
                        else:
                            idx.update(old_val, old_pks)
                            
                # 2. Add to new secondary key list
                if new_val is not None:
                    new_pks = idx.search(new_val) or []
                    if pk not in new_pks:
                        new_pks.append(pk)
                        if idx.search(new_val) is not None:
                            idx.update(new_val, new_pks)
                        else:
                            idx.insert(new_val, new_pks)

        # Update primary tree
        return self.tree.update(pk, new_row)


    def range_query(self, start_key, end_key, column_name=None):
        """
        Return all rows whose key is between start_key and end_key (inclusive).
        If column_name is provided, queries the secondary index instead of primary.
        """
        if column_name is not None:
            if column_name not in self.secondary_indexes:
                raise ValueError(f"No secondary index exists for column '{column_name}'")
            
            # Range query on secondary index yields lists of PKs for each matching secondary key
            sec_results = self.secondary_indexes[column_name].range_query(str(start_key), str(end_key))
            
            # Aggregate all valid rows and return them
            final_results = []
            seen_pks = set()  # Prevent duplicates if a PK somehow landed in multiple buckets
            
            # Format depends on your B+ tree implementation, usually range_query returns a list of (key, value) pairs or list of values
            # Assuming it returns a list of (key, value) tuples or values
            for entry in sec_results:
                # Based on standard BPlusTree, it might return list of tuples [(sec_key, pks_list), ...]
                # or just the values [pks_list_1, pks_list_2, ...]. Handle both:
                pks = entry[1] if isinstance(entry, tuple) else entry
                
                for pk in pks:
                    if pk not in seen_pks:
                        seen_pks.add(pk)
                        row = self.tree.search(pk)
                        if row:
                            final_results.append(row)
            return final_results
            
        else:
            # Standard primary tree range scan
            return self.tree.range_query(str(start_key), str(end_key))


    def get_all(self):
        """
        Return all rows sorted by primary key.
        """
        return self.tree.get_all()