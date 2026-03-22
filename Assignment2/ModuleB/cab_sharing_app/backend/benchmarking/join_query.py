import time
import random
from sqlalchemy import create_engine, text

from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")
engine = create_engine(DATABASE_URL)

def get_all_admin_ids():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT AdminID FROM ActiveRides"))
        return [row[0] for row in result]

def benchmark_join(iterations=1000):
    admin_ids = get_all_admin_ids()
    latencies = []

    print(f"\n--- JOIN Benchmark ({iterations} iterations) ---")

    query_template = """
    SELECT br.*
    FROM BookingRequests br
    JOIN ActiveRides ar ON br.RideID = ar.RideID
    WHERE ar.AdminID = :admin_id AND br.RequestStatus = 'PENDING'
    """

    with engine.connect() as conn:
        # warm-up
        conn.execute(text(query_template), {"admin_id": admin_ids[0]})

        for _ in range(iterations):
            admin_id = random.choice(admin_ids)

            start = time.perf_counter()
            conn.execute(text(query_template), {"admin_id": admin_id})
            end = time.perf_counter()

            latencies.append((end - start) * 1000)

    print(f"Avg: {sum(latencies)/len(latencies):.4f} ms")
    print(f"Min: {min(latencies):.4f} ms | Max: {max(latencies):.4f} ms")

if __name__ == "__main__":
    benchmark_join(1000)