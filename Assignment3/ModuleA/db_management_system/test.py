import unittest
import os
import tempfile
import threading
import random
from unittest.mock import patch

from database.db_manager import DatabaseManager

class TestDatabaseManagerACID(unittest.TestCase):
    
    def setUp(self):
        """Creates an isolated temporary directory for testing."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir.name)
        
        self.db = DatabaseManager()
        self.db.create_database("test_db")

    def tearDown(self):
        """Safely shuts down the DB and cleans up temporary files."""
        if hasattr(self, 'db') and self.db is not None:
            for tree in self.db.indexes.values():
                try:
                    tree.close()
                except Exception:
                    pass
            self.db.delete_database()
            
        os.chdir(self.original_cwd)
        self.test_dir.cleanup()

    # ==========================================
    # 1. ATOMICITY: Single-Operation Failure
    # ==========================================
    def test_atomicity_memory_disk_sync_on_failure(self):
        """
        Tests if the DatabaseManager rolls back memory changes if the disk 
        (B+ Tree) insertion fails, preventing memory/disk desynchronization.
        """
        self.db.create_table("Users", "id")
        self.db.insert("Users", {"id": "U1", "name": "Alice"})
        
        tree = self.db.indexes["Users"]
        
        # FIX: Patch the class (tree.__class__) instead of the instance (tree) 
        # to bypass the read-only attribute restriction.
        with patch.object(tree.__class__, 'insert', side_effect=RuntimeError("Simulated Disk Crash!")):
            try:
                self.db.insert("Users", {"id": "U2", "name": "Bob"})
            except RuntimeError:
                pass # Expected failure
                
        # VERIFY ATOMICITY:
        # If atomicity holds, Bob should NOT be in the B+ Tree, AND he should 
        # NOT be left lingering in the in-memory Table.
        in_memory_table = self.db.get_table("Users")
        
        self.assertNotIn("U2", in_memory_table.rows, 
                         "Atomicity Failed: Record exists in memory but failed on disk!")
        self.assertIsNone(self.db.search("Users", "U2"), 
                          "Atomicity Failed: Incomplete record found on disk.")

    # ==========================================
    # 2. CONSISTENCY: Heavy Thrashing
    # ==========================================
    def test_consistency_heavy_thrashing(self):
        """
        Forces rapid inserts, updates, and deletes to ensure the B+ Tree and 
        Table mappings remain structurally sound and consistent.
        """
        # Small order (3) forces extreme node splitting/merging
        self.db.create_table("Metrics", "id", order=3) 
        
        # 1. Insert 500 records
        for i in range(500):
            self.db.insert("Metrics", {"id": f"K_{i:03d}", "val": i})
            
        # 2. Delete the middle 200 records
        for i in range(150, 350):
            self.db.delete("Metrics", f"K_{i:03d}")
            
        # 3. Update the remaining records
        for i in range(150):
            self.db.update("Metrics", f"K_{i:03d}", {"val": i * 10})
        for i in range(350, 500):
            self.db.update("Metrics", f"K_{i:03d}", {"val": i * 10})
            
        # VERIFY CONSISTENCY:
        mem_table = self.db.get_table("Metrics")
        disk_results = self.db.range_query("Metrics", "K_000", "K_500")
        
        # Check counts
        self.assertEqual(len(mem_table.rows), 300, "Consistency Failed: Memory row count is wrong.")
        self.assertEqual(len(disk_results), 300, "Consistency Failed: Disk row count is wrong.")
        
        # Ensure a deleted record is truly gone from both
        self.assertNotIn("K_200", mem_table.rows)
        self.assertIsNone(self.db.search("Metrics", "K_200"))

    # ==========================================
    # 3. ISOLATION: Concurrent Race Conditions
    # ==========================================
    def test_isolation_concurrent_updates(self):
        """
        Blasts the exact same record with simultaneous updates from different threads 
        to ensure the underlying tree locks correctly and doesn't corrupt data.
        """
        self.db.create_table("Counters", "id")
        self.db.insert("Counters", {"id": "GlobalHits", "count": 0})
        
        def worker_update(thread_id, iterations):
            for i in range(iterations):
                # Blindly overwrite the row. 
                # If locking fails, the tree structure might corrupt under concurrent writes.
                self.db.update("Counters", "GlobalHits", {"count": thread_id, "iter": i})

        threads = []
        for thread_id in range(10):
            t = threading.Thread(target=worker_update, args=(thread_id, 20))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        # VERIFY ISOLATION:
        # We don't know *which* thread finished last, but the DB shouldn't have crashed,
        # and the final state in memory should perfectly match the final state on disk.
        final_mem = self.db.get_table("Counters").rows["GlobalHits"]
        final_disk = self.db.search("Counters", "GlobalHits")
        
        self.assertIsNotNone(final_disk, "Isolation Failed: Record was destroyed by concurrent writes.")
        self.assertEqual(final_mem, final_disk, "Isolation Failed: Memory and Disk desynced under load.")

    # ==========================================
    # 4. DURABILITY: Total System Restart
    # ==========================================
    def test_durability_system_restart(self):
        """
        Simulates an engine shutdown and verifies that creating a table with 
        an existing name correctly re-attaches to the persistent B+ Tree data.
        """
        self.db.create_table("Products", "id")
        self.db.insert("Products", {"id": "P1", "name": "Laptop"})
        self.db.insert("Products", {"id": "P2", "name": "Mouse"})
        
        # SIMULATE COMPLETE SYSTEM SHUTDOWN
        for tree in self.db.indexes.values():
            tree.close()
        
        # Destroy the in-memory manager
        del self.db 
        
        # BOOT UP A NEW INSTANCE
        new_db = DatabaseManager()
        new_db.create_database("test_db")
        
        # When we create the table again, it should attach to the existing ./Products.db
        new_db.create_table("Products", "id")
        
        # VERIFY DURABILITY:
        # The new DB manager should be able to read the data from disk.
        laptop = new_db.search("Products", "P1")
        self.assertIsNotNone(laptop, "Durability Failed: Committed data was lost on restart.")
        self.assertEqual(laptop["name"], "Laptop")
        
        # Clean up the new DB instance
        for tree in new_db.indexes.values():
            tree.close()

if __name__ == '__main__':
    unittest.main()