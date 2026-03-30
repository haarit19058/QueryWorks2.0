"""
Database package initialization.

Exposes main components:
- DatabaseManager
- Table
- BPlusTree
- BruteForceDB
"""

from .db_manager import DatabaseManager
from .table import Table
from .bplustree import BPlusTree

import sys, os

# Allow running scripts directly from ModuleA folder
module_dir = os.path.dirname(__file__)
if module_dir not in sys.path:
    sys.path.insert(0, module_dir)
