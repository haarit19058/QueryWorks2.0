# QueryWorks 2.0 — College Cab Sharing Portal

## Project Overview

QueryWorks 2.0 is a database systems project developed for CS 432 — Databases. The project evolves a college cab-sharing portal across four stages, moving from relational database design to a custom database engine, transaction and concurrency support, and finally a horizontally sharded deployment.

The system supports core ride-sharing workflows such as member authentication, ride creation, ride discovery, booking requests, messaging, ride history, ratings, feedback, and administrative operations.

### Project Evolution

| Assignment | Focus | Main Outcome |
|---|---|---|
| **Assignment 1** | Database Design | Designed the relational schema and system architecture for the cab-sharing portal |
| **Assignment 2** | Database Engine + Full Stack Application | Built a custom B+ Tree based database layer and a web application backed by MySQL |
| **Assignment 3** | Transactions, ACID & Concurrency | Extended the custom database with WAL, recovery, locking and transactions; tested concurrent web usage and race conditions |
| **Assignment 4** | Distributed Databases | Added horizontal sharding, shard-aware query routing and migration across three MySQL shards |

---

## 1. Assignment 1 — Database Design

The project began with the design of a relational database for a college cab-sharing platform.

The schema models:

- Members
- Active rides
- Booking requests
- Cancellations
- Member ratings and statistics
- Message history
- Ride feedback
- Ride history
- Ride-passenger mappings
- Vehicles

The design covered the main application workflows including authentication, ride creation, ride search, booking, cancellation, communication, history, ratings and feedback.

### Design Work

The system architecture and database design were developed collaboratively. The project included UML artifacts to represent the system structure and behavior.

---

## 2. Assignment 2 — Custom Database Engine & Full-Stack Application

Assignment 2 expanded the project into two major modules.

### Module A — B+ Tree Database Engine

A lightweight database engine was implemented from scratch in Python using a **B+ Tree** as its primary indexing and storage structure.

The implementation contains:

- Internal and leaf B+ Tree nodes
- Insertion with node splitting
- Deletion with borrowing and merging
- Exact-key search
- Range queries using linked leaf nodes
- Updates
- Table abstraction
- Database manager
- Brute-force baseline for comparison
- Tree visualization using Graphviz

The B+ Tree supports approximately:

- `O(log n)` insertion, search and deletion
- `O(log n + k)` range queries, where `k` is the number of returned records

The implementation was benchmarked against a brute-force approach using the ride-sharing dataset.

### Module B — Web Application

A full-stack version of the cab-sharing portal was developed with:

**Frontend**

- React
- TypeScript
- Vite
- Tailwind CSS

**Backend**

- FastAPI
- SQLAlchemy
- MySQL
- JWT-based session handling
- Google OAuth integration

The application provides interfaces for:

- Login and signup
- Available rides
- Ride creation
- User's rides
- Ride history
- Member profiles
- Messaging/chat
- Booking requests
- Administrative functionality

The backend exposes REST APIs for the application's database operations.

### Database Optimization

The application also explored relational database optimization through indexes and query-plan analysis, including indexes on frequently queried attributes such as:

- `Members.Email`
- `BookingRequests.RequestStatus`
- `(MessageHistory.RideID, MessageHistory.Timestamp)`

Query performance was evaluated using benchmark comparisons and `EXPLAIN` plans.

---

## 3. Assignment 3 — Transactions, ACID & Concurrent Usage

Assignment 3 extended the database system to address reliability and concurrent execution.

### Module A — Transactional Custom Database

The custom B+ Tree database was extended with transaction-management functionality including:

- Transaction Manager
- Write-Ahead Logging (WAL)
- Lock Manager
- Recovery Manager
- `BEGIN`
- `COMMIT`
- `ROLLBACK`

The system addressed the four ACID properties:

### Atomicity

Write-Ahead Logging was used to support logical UNDO operations and rollback of incomplete transactions.

### Consistency

Schema validation and the B+ Tree storage layer were used to preserve database constraints and maintain a single storage path.

### Isolation

**Strict Two-Phase Locking (S2PL)** with record-level shared/exclusive locks was implemented, with lock timeouts to prevent transactions from waiting indefinitely.

### Durability

Committed changes were synchronously flushed using `fsync`. Recovery used REDO/UNDO processing, with periodic checkpoints.

### Concurrent Transaction Testing

The transactional system was tested using multi-table transactions executed across concurrent threads.

The reported benchmark for the custom database was approximately:

- **1.65 s total execution time**
- **303.06 transactions/second**

The corresponding MySQL + SQLAlchemy implementation was reported at:

- **2.39 s total execution time**
- **208.89 transactions/second**

These results were evaluated in the context of the project's custom in-process database architecture rather than as a general claim that the custom engine is faster than production database systems.

### Module B — Web Concurrency & Race Conditions

The web application was tested under concurrent workloads.

Tests covered:

- Concurrent reads
- Concurrent booking requests
- Concurrent messaging
- Concurrent ride creation

A Locust workload of **100 concurrent users** generated:

- 1269 requests
- 0 reported failures
- ~10.65 requests/second
- Median response time of approximately 6.3 seconds
- Average response time of approximately 8.25 seconds

A larger **500-user** workload exposed a connection-pool limitation, with the configured pool reaching its maximum capacity.

### Race Condition Fixes

Two important application-level race conditions were identified and addressed.

**Booking approval race**

Two concurrent booking approvals could observe the same available-seat count and both attempt to confirm a booking. The ride row was protected using `SELECT ... FOR UPDATE` / SQLAlchemy `with_for_update()` so that competing approvals serialize access to the relevant row.

**Rating update race**

Concurrent rating updates could suffer from stale read-modify-write behavior. The relevant member-stat row was locked using `with_for_update()` before updating the aggregate statistics.

### Failure Simulation

Ride completion, which moves a ride from `ActiveRides` to `RideHistory`, was tested as a transactional operation. Forced interruption during the operation was used to verify rollback behavior.

---

## 4. Assignment 4 — Horizontal Sharding & Distributed Query Routing

The final stage introduced horizontal scaling by distributing the database across **three simulated MySQL shards** running in Docker containers.

The design uses a hybrid partitioning strategy.

### Hash-Based Partitioning

Core member-related data is assigned to a shard using:

`SHA256(MemberID) % number_of_shards`

This is used for tables such as:

- Members
- MemberStats
- Cancellations

### Directory-Based Partitioning

Ride-related dependent tables use a global mapping:

`RideID → Shard_ID`

The directory allows the system to determine which shard contains a particular ride and route dependent queries accordingly.

Tables using ride-based routing include:

- ActiveRides
- RideHistory
- BookingRequests
- MessageHistory
- RidePassengerMap
- MemberRating
- RideFeedback

Vehicles are replicated across all three shards.

### Data Migration

Migration was performed in phases:

1. Migrate independent tables using hash-based placement
2. Migrate rides and build the global ride directory
3. Migrate dependent ride tables using the directory

Integrity checks included:

- Row-count comparison
- Duplicate primary-key checks
- Column-by-column comparison
- Distribution checks across shards

### Query Routing

The distributed system supports shard-aware routing for operations such as:

- Member lookup
- Ride lookup
- New member creation
- Ride creation
- Range queries across shards

For range queries, requests can be sent to multiple shards in parallel and the results merged.

The design also considers partial-result behavior when a shard becomes unavailable.

---

# Architecture

The project can be viewed as a progression through four database-system layers:

```text
Assignment 1
Relational Schema & System Design
            │
            ▼
Assignment 2
Custom B+ Tree DB + Full-Stack Web Application
            │
            ▼
Assignment 3
Transactions + WAL + Recovery + Locking
            │
            ▼
Assignment 4
Horizontal Sharding + Distributed Query Routing

The overall technology stack includes:

- **Python**
- **B+ Trees**
- **FastAPI**
- **SQLAlchemy**
- **MySQL**
- **React**
- **TypeScript**
- **Vite**
- **Tailwind CSS**
- **JWT**
- **Google OAuth**
- **Locust**
- **Docker**
- **Graphviz**

---
```
# Key Technical Concepts Demonstrated

- Relational database design
- ER/UML-based system modelling
- B+ Tree indexing
- Database storage abstractions
- CRUD operations
- Query optimization
- SQL indexes
- `EXPLAIN` query plans
- Transactions
- ACID properties
- Write-Ahead Logging
- REDO/UNDO recovery
- Strict Two-Phase Locking
- Record-level concurrency control
- Race-condition analysis
- Concurrent workload testing
- Connection-pool behavior
- Failure simulation
- Horizontal sharding
- Hash partitioning
- Directory-based partitioning
- Distributed query routing

---
```
```
# Repository Structure

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
└── Project_summary.md         # This file
```
# Conclusion

QueryWorks 2.0 demonstrates the evolution of a database-backed application through multiple layers of database-system design and implementation.

Starting from a relational schema, the project progresses through:

database design → indexing and storage → transactions and recovery → concurrency control → performance testing → horizontal sharding and distributed query routing.

The project combines theoretical database concepts with practical implementation, testing, benchmarking, and system-level design considerations.