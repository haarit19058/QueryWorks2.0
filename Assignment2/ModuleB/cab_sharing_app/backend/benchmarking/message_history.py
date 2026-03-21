import time
import random
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")
engine = create_engine(DATABASE_URL)

def get_all_ride_ids():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT RideID FROM MessageHistory"))
        return [row[0] for row in result]

def benchmark_messages(iterations=1000):
    ride_ids = get_all_ride_ids()
    latencies = []

    print(f"\n--- MessageHistory Benchmark ({iterations} iterations) ---")

    query = """
    SELECT *
    FROM MessageHistory
    WHERE RideID = :ride_id
    ORDER BY Timestamp ASC
    """

    with engine.connect() as conn:
        # warm-up
        conn.execute(text(query), {"ride_id": ride_ids[0]})

        for _ in range(iterations):
            ride_id = random.choice(ride_ids)

            start = time.perf_counter()
            conn.execute(text(query), {"ride_id": ride_id})
            end = time.perf_counter()

            latencies.append((end - start) * 1000)

    print(f"Avg: {sum(latencies)/len(latencies):.4f} ms")
    print(f"Min: {min(latencies):.4f} ms | Max: {max(latencies):.4f} ms")

if __name__ == "__main__":
    benchmark_messages(1000)