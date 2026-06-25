# QueryWorks 2.0

## CS 432 Databases | Track 1 | College Cab Sharing Portal

A semester-long project that builds a complete, student-only cab sharing platform from the ground up, including a custom database engine written from scratch in Python.

---

## Problem Statement

Students travelling to and from college often struggle with high travel costs and limited public transport options. Trying to share rides using informal methods, such as WhatsApp groups, is messy. It leads to confusion, double bookings, sudden cancellations, and safety concerns because you cannot verify who you are travelling with. There is no proper system to check available rides in real time, prevent too many people from booking the same seat, or keep a history of past trips. This makes travel planning stressful, expensive, and inefficient for students.

## Current Solutions

Currently, most students rely on WhatsApp groups, college notice boards, or general taxi apps that are not designed for student carpooling. These methods lack essential safety features, such as verifying that the passenger is actually a student from the same college. They also fail to handle crucial tasks, such as automatically removing old ride requests or strictly limiting the number of seats. While general apps work for solo rides, they do not support campus-specific routes or track shared college trips. As a result, existing solutions fail to offer a safe, organised, and budget-friendly way for students to share rides.

## Our Solution

We built **IITGN Pool**, a cab sharing portal exclusive to our college community. Access is gated behind college-verified accounts, so every ride creator and passenger on the platform is a genuine student from the same campus. On top of that trust layer, the application offers:

- **College-only verified sign-up and login** so you always know who you are sharing a ride with.
- **Post and discover rides in real time**, with strict seat limits enforced at the database level so the same seat can never be double-booked.
- **Interactive map and location autocomplete** for picking pickup and drop-off points along campus routes.
- **Booking requests and seat management**, where ride owners approve or reject passengers and remaining seats update instantly.
- **In-app chat** between co-passengers so plans, pickup points, and timing are coordinated in one place instead of scattered across messaging apps.
- **Ratings and feedback** for members and rides, building a reputation system that rewards reliable students.
- **Ride history** for both ride admins and passengers, giving every user a record of past trips.
- **An admin dashboard** for oversight of users, rides, and platform activity.

The application itself is backed by a standard **SQL** database. Alongside it, as a study exercise, we built our own **B+ tree storage engine from scratch** purely for testing and experimentation: to understand how indexing, ACID guarantees, write-ahead logging, locking, and sharding work under the hood, and to benchmark these ideas against the SQL backend. The B+ tree engine is not what runs the live app; it is our own implementation used to explore and validate database internals.

---

## Repository Structure

```text
QueryWorks2.0/
├── Assignment2/
│   ├── ModuleA/      # Custom B+ tree DBMS engine (from scratch)
│   └── ModuleB/      # First version of the ride sharing app
├── Assignment3/
│   ├── ModuleA/      # B+ tree engine extended with ACID properties
│   └── ModuleB/      # ACID-backed app + backend stress testing
├── Assignment4/      # Final sharded application (horizontal scaling)
└── README.md         # This file
```

### Assignment 2 - Foundations

**`Assignment2/ModuleA/` - Custom B+ Tree DBMS**
A lightweight database management system built entirely in Python, using a B+ tree as the core indexing structure. This is a study and testing implementation, separate from the SQL backend that powers the app; we built it to understand and benchmark indexing internals. Supports named databases and tables with schema validation, insert/delete/search/update/range queries, automatic node splitting and merging, performance benchmarking against a brute-force baseline, and Graphviz tree visualisations. Includes a Jupyter report notebook documenting the design and benchmarks.

**`Assignment2/ModuleB/` - First Version of the Ride Sharing App**
The initial end-to-end ride sharing application, with a backend, a frontend, and the `RideShare.sql` schema. Includes a `benchmarking/` suite that studies query performance (email lookups, joins, message queries) and demonstrates the N+1 query problem, plus audit logging.

### Assignment 3 - Reliability (ACID)

**`Assignment3/ModuleA/` - B+ Tree Engine with ACID Properties**
Our study B+ tree engine upgraded to provide full transactional guarantees, used to test and benchmark ACID concepts (again, separate from the app's SQL backend):

- `bplustree.py`, `table.py`, `db_manager.py` - the indexed storage layer.
- `transaction.py` - transaction management.
- `lock_manager.py` - concurrency control and locking.
- `wal.py` - write-ahead logging for durability.
- `recovery.py` - crash recovery from the log.
- `acid_test.py`, `benchmarking.py` - ACID correctness tests and throughput benchmarks (results in `acid_throughput_comparison.png`).
- `storage/`, `benchmark_storage/` - persisted B+ tree tables for the test and benchmark databases.

**`Assignment3/ModuleB/` - ACID App and Backend Stress Testing**
The ride sharing application on its SQL backend, hardened for ACID behaviour and stress tested under concurrent load. Contains the backend, frontend, SQL, and a `benchmarking/` suite, with API documentation in the module.

### Assignment 4 - Scale (Sharding)

**`Assignment4/` - Final Sharded Application**
The complete application extended for horizontal scaling through directory-based data sharding across multiple simulated nodes.

- `app/backend/` - FastAPI-style backend with `main.py` (API router with shard-key extraction and cross-shard aggregation), `migration.py` (partitions the dataset into shards with no loss or duplication), `models.py`, `schemas.py`, `ride_shard_directory.json` (the partition routing table), `admin.json`, API docs (`API.md`), tests, and utilities.
- `app/frontend/` - React + TypeScript + Vite client. Pages include Login, SignUp, Add Ride, Available Rides, Your Rides, Ride History, Profile, and an Admin page. Components include the map, location autocomplete, navbar, chat drawer, and an admin route guard.
- `sql/` - `schema.sql` and `dml.sql` for the sharded data model.

---

## Team Details

| Name | Roll Number |
| --- | --- |
| Vedant Acharya | 23110010 |
| Haarit Chavda | 23110077 |
| Darpana Desai | 23110085 |
| Rahul Khichar | 23110264 |
| Akshat Shah | 23110293 |
