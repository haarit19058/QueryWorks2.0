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

with open("schema.sql", "r") as file:
    # Split by semicolon to handle multiple SQL statements
    schema_queries = file.read().split(';')
print(schema_queries)

for i, url in enumerate(urls):
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            for query in schema_queries:
                clean_query = query.strip()
                if clean_query:  # Skip empty strings
                    try:
                        conn.execute(text(clean_query))
                        conn.commit()
                    except Exception as sql_e:
                        print(f"Error executing statement: {clean_query[:50]}... \n{sql_e}")

            print(f"Schema applied to Shard {i} ✅")
    except Exception as e:
        print(f"Shard {i} ❌ FAILED: {e}")

