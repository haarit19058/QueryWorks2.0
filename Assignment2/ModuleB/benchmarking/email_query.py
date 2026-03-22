import time
import random
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")
engine = create_engine(DATABASE_URL)

def get_all_emails():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT Email FROM Members"))
        return [row[0] for row in result]

def benchmark_random_email(iterations=1000):
    emails = get_all_emails()
    latencies = []

    print(f"\n--- Random Email Benchmark ({iterations} requests) ---")

    with engine.connect() as conn:
        # warm-up
        conn.execute(text(f"SELECT * FROM Members WHERE Email = '{emails[0]}'"))

        for _ in range(iterations):
            email = random.choice(emails)
            query = f"SELECT * FROM Members WHERE Email = '{email}'"

            start = time.perf_counter()
            conn.execute(text(query))
            end = time.perf_counter()

            latencies.append((end - start) * 1000)

    print(f"Avg: {sum(latencies)/len(latencies):.4f} ms")
    print(f"Min: {min(latencies):.4f} ms | Max: {max(latencies):.4f} ms")

if __name__ == "__main__":
    benchmark_random_email(1000)