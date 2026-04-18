# QueryWorks 2.0 Backend

This is the backend service for the sharded QueryWorks 2.0 application. It is built using FastAPI and interacts with multiple simulated database nodes based on our sharding strategy.

## File Breakdown

* **`main.py`**: The application's entry point and API router. Responsible for receiving requests and interpreting the Shard Key from parameters or payloads to route operations to the correct data node. When performing range queries, it aggregates data across multiple shards.
* **`migration.py`**: Script used to safely extract existing data from the single monolithic system and distribute it into partitioned shard tables based on the directory definitions.
* **`models.py`**: Defines database structure mappings or ORM models.
* **`schemas.py`**: Defines Pydantic models for request and response validation, ensuring uniform data structures for APIs.
* **`ride_shard_directory.json`**: Implements Directory-Based Partitioning. This acts as a lookup file mapping specific shard keys (like Region or User ID ranges) to specific database node connections.
* **`.env`**: Stores sensitive database configurations, including connection URLs for multiple discrete shards.
* **`requirements.txt`**: Python dependencies required (FastAPI, Uvicorn, Database Drivers, etc.).
* **`API.md`**: Documentation for the available REST endpoints and their payload shapes.
* **`admin.json`**: Initial configuration file for system admins or default parameters.
* **`tables/`**: Folder containing raw CSV dump data files simulating legacy tables.
* **`tests/`**: Suite of scripts validating concurrency control, sharding edge cases, and failure recovery.
* **`utils/`**: Helper methods like DDL scripts, hash functions, and patching utilities.

## How to Run (from the repository root directory)

Open your terminal at the root directory of Assignment 4 (`Assignment4/`), then run:

### Setup & Activation

1. **Install dependencies (only needed once):**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations:**
   Make sure you have migrated the data to multiple shards first.
   ```bash
   python migration.py
   ```

3. **Start the server:**
   Use Uvicorn to host the FastAPI application, specifying the path to `main.py`.
   ```bash
   uvicorn main:app --reload
   ```
