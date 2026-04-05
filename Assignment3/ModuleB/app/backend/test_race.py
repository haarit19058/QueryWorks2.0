import asyncio
import httpx
import os
import threading
import requests as sync_requests  # Add this
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

BASE_URL = "http://localhost:8000"

load_dotenv()
DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("SQLALCHEMY_DATABASE_URL is not set")

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("SELECT MemberID FROM Members"))
    MEMBER_IDS = [row[0] for row in result]

# ✅ Synchronous approval using threading.Barrier
def approve_with_barrier(req_id, admin_id, barrier, results, index):
    barrier.wait()  # Both threads pause here until BOTH are ready, then fire together
    r = sync_requests.patch(
        f"{BASE_URL}/booking-requests/{req_id}",
        json={"RequestStatus": "APPROVED"},
        headers={"X-Test-User-ID": str(admin_id)}
    )
    results[index] = r

async def simulate_race_condition():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Step 1: Create ride
        print("Setup: Creating ride...")
        start_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        admin_id = MEMBER_IDS[0]

        ride_payload = {
            "AdminID": admin_id,
            "Source": "Library",
            "Destination": "Hostel",
            "StartTime": start_time,
            "AvailableSeats": 1,
            "VehicleType": "Bike",
            "FemaleOnly": False,
            "EstimatedTime": 15
        }

        resp = await client.post("/rides", json=ride_payload, headers={"X-Test-User-ID": str(admin_id)})
        if resp.status_code != 200:
            print("Failed to create ride:", resp.text)
            return

        ride = resp.json()
        ride_id = ride["RideID"]
        print(f"Ride Created: {ride_id} with {ride['AvailableSeats']} available seats.")

        # Step 2 & 3: Both passengers request to join
        passenger_1 = MEMBER_IDS[1]
        passenger_2 = MEMBER_IDS[2]

        req1 = await client.post("/booking-requests", json={"RideID": ride_id}, headers={"X-Test-User-ID": str(passenger_1)})
        req2 = await client.post("/booking-requests", json={"RideID": ride_id}, headers={"X-Test-User-ID": str(passenger_2)})

        req_id_1 = req1.json()["RequestID"]
        req_id_2 = req2.json()["RequestID"]

        print(f"Booking Requests Created: {req_id_1} and {req_id_2}")

        # Step 4: ✅ Use threading.Barrier to fire BOTH approvals at the exact same instant
        print("Admin approving BOTH requests simultaneously...")

        barrier = threading.Barrier(2)  # Wait for 2 threads before releasing
        results = [None, None]

        t1 = threading.Thread(target=approve_with_barrier, args=(req_id_1, admin_id, barrier, results, 0))
        t2 = threading.Thread(target=approve_with_barrier, args=(req_id_2, admin_id, barrier, results, 1))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        for i, r in enumerate(results):
            print(f"Approval response {i+1}: {r.status_code} - {r.text}")

        # Step 5: Verify DB state
        print("-" * 50)
        print("Checking database for final state...")

    with engine.connect() as conn:
        # Check seats
        result = conn.execute(text(
            f"SELECT AvailableSeats, PassengerCount FROM ActiveRides WHERE RideID = '{ride_id}'"
        ))
        row = result.fetchone()
        current_seats, current_passengers = row[0], row[1]
        print(f"AvailableSeats: {current_seats}, PassengerCount: {current_passengers}")

        # ✅ Check the REAL corruption — how many confirmed passengers exist
        result2 = conn.execute(text(
            f"SELECT COUNT(*) FROM RidePassengerMap WHERE RideID = '{ride_id}' AND IsConfirmed = TRUE"
        ))
        confirmed_count = result2.fetchone()[0]
        print(f"Confirmed passengers in RidePassengerMap: {confirmed_count}")

        # A bike has MaxCapacity=2, creator takes 1 seat, so only 1 more allowed
        if confirmed_count > 2:  # MaxCapacity of bike
            print("🚨 RACE CONDITION CONFIRMED: More passengers than vehicle capacity!")
        elif current_passengers != confirmed_count:
            print(f"🚨 DATA INCONSISTENCY: PassengerCount={current_passengers} but actual confirmed={confirmed_count}")
        else:
            print("✅ No corruption detected")

if __name__ == "__main__":
    asyncio.run(simulate_race_condition())