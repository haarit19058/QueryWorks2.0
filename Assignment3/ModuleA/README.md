# Lightweight DBMS with B+ Tree Index

## Overview

This project implements a lightweight **Database Management System (DBMS)** using a **B+ Tree** as the core indexing structure, built entirely from scratch in Python.

The system supports:
- Named database and table creation with schema validation
- Insertion, deletion, search, update, and range queries
- Efficient B+ Tree indexing with automatic node splitting and merging
- Performance benchmarking against a brute-force baseline
- Tree structure visualization using Graphviz

---

## Project Structure

```
Module_A/
├── db_management_system/
│   ├── database/
│   │   ├── __init__.py          # Package exports
│   │   ├── bplustree.py         # B+ Tree implementation
│   │   ├── bruteforce.py        # BruteForceDB (baseline)
│   │   ├── db_manager.py        # Database Manager
│   │   └── table.py             # Table abstraction
│   │
│   ├── tables/                  # CSV files for all 11 tables
│   │
│   ├── bptree_images/           # Generated B+ Tree visualizations (PNG)
│   │
│   ├── report.ipynb             # Main report and demonstration notebook
│   ├── performance_comparison.png
│   ├── random_workload.png
│   └── requirements.txt
└── README.md
```

---

## Components

### `bplustree.py` — B+ Tree Engine

The core data structure. Implements a self-balancing B+ Tree with:

- **`BPlusTreeNode` / `LeafNode` / `InternalNode`** — node classes
- **`insert`** — inserts key-value pair with automatic node splitting
- **`delete`** — removes a key with underflow handling (borrow or merge)
- **`search`** — exact key lookup via binary search at leaf level
- **`range_query`** — efficient range scan using the linked leaf list
- **`update`** — modifies the value for an existing key
- **`get_all`** — returns all key-value pairs in sorted order
- **`visualize_tree`** — renders the tree to a Graphviz PNG file

Leaf nodes are connected as a **doubly-linked list**, enabling O(log n + k) range queries.

---

### `table.py` — Table Abstraction

Wraps the B+ Tree with a table-level interface:

- Stores rows as `{primary_key: row_dict}`
- Supports optional **schema validation** (column names and data types)
- Operations: `insert`, `delete`, `get`, `update`, `range_query`, `get_all`

---

### `db_manager.py` — Database Manager

Top-level API that manages multiple tables and keeps each table's B+ Tree index in sync:

| Method | Description |
|---|---|
| `create_database(name)` | Register a named database |
| `list_databases()` | List registered databases |
| `create_table(name, pk, schema, order)` | Create table + B+ Tree index |
| `list_tables()` | List all tables in the database |
| `insert(table, row)` | Insert into table and index |
| `search(table, key)` | Exact lookup via B+ Tree |
| `update(table, key, row)` | Update record in table and index |
| `delete(table, key)` | Remove from table and index |
| `range_query(table, start, end)` | Range scan via B+ Tree |

---

### `bruteforce.py` — BruteForceDB

A simple list-based database used as a **performance comparison baseline**:

- `insert` — O(1) append
- `search` — O(n) linear scan
- `delete` — O(n) scan and remove
- `range_query` — O(n) full scan with filter

---

## Time Complexity

| Operation | B+ Tree | Brute Force |
|---|---|---|
| Insert | O(log n) | O(1) |
| Search | O(log n) | O(n) |
| Delete | O(log n) | O(n) |
| Range Query | O(log n + k) | O(n) |

---

## Requirements

- Python 3.8+
- [Graphviz](https://graphviz.org/download/) must be installed on your system (not just the Python package)

Install Python dependencies:

```bash
pip install pandas numpy matplotlib graphviz jupyter
```

---

## Steps to Execute

### 1. Clone / download the repository

```bash
git clone <your-repo-url>
cd Module_A/db_management_system
```

### 2. Install dependencies

```bash
pip install pandas numpy matplotlib graphviz jupyter
```

> **Important:** Also install the Graphviz binary for your OS:
> - **Windows:** Download from https://graphviz.org/download/ and add to PATH
> - **macOS:** `brew install graphviz`
> - **Linux:** `sudo apt install graphviz`

### 3. Launch the notebook

```bash
jupyter notebook report.ipynb
```

### 4. Run all cells in order

In Jupyter: **Kernel → Restart & Run All**

The notebook will:
1. Initialize the `rideshare` database
2. Create and populate the `Vehicles` table step by step (schema → create → insert)
3. Load the remaining 10 tables from CSV files in `tables/`
4. Demonstrate search, range query, insert, update, and delete on different tables
5. Generate B+ Tree visualizations saved to `bptree_images/`
6. Run performance benchmarks and display comparison plots
7. Run the random workload test with a summary table and bar chart
8. Measure and compare memory usage

---

## Example Usage (Standalone)

```python
from database import DatabaseManager

# 1. Create database
db = DatabaseManager()
db.create_database('rideshare')

# 2. Define schema and create table
schema = {'VehicleID': int, 'VehicleType': str, 'MaxCapacity': int}
db.create_table('Vehicles', 'VehicleID', schema=schema, order=5)

# 3. Insert records
db.insert('Vehicles', {'VehicleID': 1, 'VehicleType': 'Bike',    'MaxCapacity': 1})
db.insert('Vehicles', {'VehicleID': 2, 'VehicleType': 'Mini Cab','MaxCapacity': 4})
db.insert('Vehicles', {'VehicleID': 3, 'VehicleType': 'SUV Cab', 'MaxCapacity': 6})

# 4. Search
print(db.search('Vehicles', 2))

# 5. Range query
print(db.range_query('Vehicles', 1, 3))

# 6. Update
db.update('Vehicles', 1, {'VehicleID': 1, 'VehicleType': 'E-Bike', 'MaxCapacity': 1})

# 7. Delete
db.delete('Vehicles', 2)

# 8. Visualize
db.indexes['Vehicles'].visualize_tree('vehicles_tree')
# Output: vehicles_tree.png

# 9. List tables
print(db.list_tables())  # ['Vehicles']
```

---

## Visualization

B+ Tree visualizations are generated using [Graphviz](https://graphviz.org/) and saved as PNG files in `bptree_images/`.

- **Blue nodes** — internal nodes (separator keys)
- **Green nodes** — leaf nodes (key-value pairs)
- **Solid arrows** — parent-child relationships
- **Dashed grey arrows** — doubly-linked leaf list

All images are saved at full resolution and can be opened outside the notebook for detailed inspection.

---

## Video Demonstration

https://drive.google.com/file/d/1I9zkvqs1rKnElnve3mL8sAIaEZh10ggV/view?usp=sharing