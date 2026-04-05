## Folder structure Module A

```bash
ModuleA
├── acid_test.py
├── acid_throughput_comparison.png
├── benchmarking.py
├── benchmark_storage
│   ├── BenchmarkDB_ActiveRides_bplustree.pkl
│   ├── BenchmarkDB_Members_bplustree.pkl
│   ├── BenchmarkDB_Vehicles_bplustree.pkl
│   └── sqlite_bench.db
├── bplustree.py
├── db_manager.py
├── init_db.py
├── __init__.py
├── lock_manager.py
├── recovery.py
├── storage
│   ├── QueryWorksDB_ActiveRides_bplustree.pkl
│   ├── QueryWorksDB_BookingRequests_bplustree.pkl
│   ├── QueryWorksDB_Cancellation_bplustree.pkl
│   ├── QueryWorksDB_MemberRatings_bplustree.pkl
│   ├── QueryWorksDB_Members_bplustree.pkl
│   ├── QueryWorksDB_MemberStats_bplustree.pkl
│   ├── QueryWorksDB_MessageHistory_bplustree.pkl
│   ├── QueryWorksDB_RideFeedback_bplustree.pkl
│   ├── QueryWorksDB_RideHistory_bplustree.pkl
│   ├── QueryWorksDB_RidePassengerMap_bplustree.pkl
│   └── QueryWorksDB_Vehicles_bplustree.pkl
├── table.py
├── transaction.py
└── wal.py
```
## Folder structure Module B
```bash
ModuleB/app/backend/
├── admin.json
├── API.md # API documentation
├── main.py # Main server
├── failure_test.py # failure test file
├── locustfile.py # stress test file
├── my_test_exceptions.csv
├── my_test_failures.csv
├── my_test_stats.csv
├── my_test_stats_history.csv
├── test_concurrency.py # concurrency test
├── test_race_2.py # race condition 2 test
└── test_race.py # race condition test
```

