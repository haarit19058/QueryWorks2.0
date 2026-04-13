from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

SHARD0_URL = os.environ.get("SHARD0_DATABASE_URL")
SHARD1_URL = os.environ.get("SHARD1_DATABASE_URL")
SHARD2_URL = os.environ.get("SHARD2_DATABASE_URL")


urls = [
    SHARD0_URL,
    SHARD1_URL,
    SHARD2_URL
]

for i, url in enumerate(urls):
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            # 1. Identify current user and database
            session_info = conn.execute(text("SELECT USER(), DATABASE()")).fetchone()
            current_user, current_db = session_info

            print(f"\n--- Shard {i} Connected ---")
            print(f"User: {current_user}")
            print(f"Database: {current_db}")

            # 2. List tables
            result = conn.execute(text("SHOW TABLES")).fetchall()
            for row in result:
                print(row)
            
            result = conn.execute(text("SELECT @@hostname, @@port;")).fetchone()
            host, port = result
            
            print(f"\n--- Shard {i} Connection Details ---")
            print(f"Host (Server Name): {host}")
            print(f"Port: {port}")

            print(f"Shard {i} ✅ OK")

    except Exception as e:
        print(f"Shard {i} ❌ FAILED: {e}")