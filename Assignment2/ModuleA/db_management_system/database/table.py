import pandas as pd


class Table:
    """
    Represents a database table.
    Stores rows as a dictionary: {primary_key: row_data}
    """
    
    def __init__(self, name, key_column, schema=None):
        self.name       = name
        self.key_column = key_column
        self.schema     = schema or {}  
        self.rows       = {}
  
        
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
        Load data from CSV into table.
        Each row is stored using key_column as key.
        """
        df = pd.read_csv(path)

        for _, row in df.iterrows():
            key = row[self.key_column]
            self.rows[key] = row.to_dict()


    def insert(self, row):
        """
        Insert a row into the table.
        """
        key = row[self.key_column]
        self.rows[key] = row


    def delete(self, key):
        """
        Delete row by primary key.
        """
        if key in self.rows:
            del self.rows[key]


    def get(self, key):
        """
        Retrieve row by key.
        """
        return self.rows.get(key)
    
    
    def update(self, key, new_row):
        """
        Update a row by primary key. Returns True if found.
        """
        if key in self.rows:
            self.rows[key] = new_row
            return True
        
        return False


    def range_query(self, start_key, end_key):
        """
        Return all rows whose key is between start_key and end_key (inclusive).
        """
        return {
            k: v for k, v in self.rows.items()
            if start_key <= k <= end_key
        }


    def get_all(self):
        """
        Return all rows sorted by primary key.
        """
        return [(k, self.rows[k]) for k in sorted(self.rows)]
