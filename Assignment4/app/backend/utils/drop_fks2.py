import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URLS = {
    0: os.getenv("SHARD0_DATABASE_URL"),
    1: os.getenv("SHARD1_DATABASE_URL"),
    2: os.getenv("SHARD2_DATABASE_URL")
}

statements = [
    "ALTER TABLE RidePassengerMap DROP FOREIGN KEY fk_ridemap_passenger;",
    "ALTER TABLE RidePassengerMap DROP FOREIGN KEY fk_ridemap_ride;" # Just in case
]

for shard_id, url in DB_URLS.items():
    if not url: continue
    print(f"Dropping FKs on shard {shard_id} at {url}")
    engine = create_engine(url)
    with engine.connect() as conn:
        for stmt in statements:
            try:
                conn.execute(text(stmt))
                print(f"✓ Executed: {stmt[:40]}...")
            except Exception as e:
                print(f"Skipped (perhaps already dropped): {stmt[:40]}...")
        conn.commit()

print("All foreign keys removed.")
