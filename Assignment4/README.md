# QueryWorks 2.0 - Assignment 4: Data Sharding

## Overview
This assignment focuses on extending the developed application to support horizontal scaling through logical data partitioning (sharding). The system implements a directory-based sharding strategy across multiple simulated nodes to gracefully handle large datasets.

## Directory Structure (Backend)
```text
.
├── admin.json
├── API.md
├── __init__.py
├── main.py
├── migration.py
├── models.py
├── __pycache__
├── requirements.txt
├── ride_shard_directory.json
├── schemas.py
├── tables/
├── test.py
├── tests/
└── utils/
```

## Directory Structure (Frontend)
```text
.
├── .env
├── .gitignore
├── App.tsx
├── index.html
├── index.tsx
├── metadata.json
├── package.json
├── README.md
├── store.tsx
├── tsconfig.json
├── types.ts
├── vite.config.ts
├── components/
├── lib/
└── pages/
```

## Sharding Implementation Highlights

* **`ride_shard_directory.json`**: Implements **Directory-Based Partitioning**. This acts as a routing lookup table that maps shard keys (or key ranges) to a specific shard. It provides flexibility for data redistribution.
* **`migration.py`**: The main migration script responsible for partitioning the initial dataset. It reads the existing data and writes subsets into the appropriate shard tables based on the directory mapping, ensuring no data loss or duplication.
* **`main.py`**: The application's entry point and API router. Updated logic extracts the Shard Key from incoming payloads/parameters. It correctly routes lookups and inserts to the designated shard, and aggregates the results for range queries spanning multiple shards.
* **`.env`**: Configuration file updated to include connection strings and environments for multiple simulated database shards, ensuring distinct shards operate securely and concurrently.

---

## Setup Instructions

### 1. Environment Variables

Add a `.env` file in the following directories (Note: Use the `.env` format required for the sharded architecture):

* `app/backend`
* `app/frontend`

---

## Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd app/backend
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the backend server:

   ```bash
   uvicorn main:app --reload
   ```

---

## Frontend Setup

> **Prerequisite:** Make sure Node.js is installed on your system.

1. Navigate to the frontend directory:

   ```bash
   cd app/frontend
   ```

2. Install the Node dependencies:

   ```bash
   npm install 
   ```

3. Start the development server:

   ```bash
   npm run dev 
   ```