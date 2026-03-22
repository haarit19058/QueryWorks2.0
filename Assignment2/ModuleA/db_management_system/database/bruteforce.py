class BruteForceDB:
    """
    Simple brute-force database implementation using a Python list.
    Used for performance comparison with B+ Tree.
    """

    def __init__(self):
        # Stores all keys in a simple list (no indexing)
        self.data = []

    def insert(self, key):
        # Insert key into list (O(1))
        self.data.append(key)

    def search(self, key):
        # Linear search → O(n)
        return key in self.data

    def delete(self, key):
        # Remove key if present → O(n)
        if key in self.data:
            self.data.remove(key)

    def range_query(self, start, end):
        # Scan entire list and filter keys in range → O(n)
        return [k for k in self.data if start <= k <= end]