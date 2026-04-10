import threading
import requests
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")
engine = create_engine(DATABASE_URL)
BASE_URL = "http://localhost:8000"

with engine.connect() as conn:
    result = conn.execute(text("SELECT MemberID FROM Members"))
    MEMBER_IDS = [row[0] for row in result]

def test_concurrent_ratings():
    print("\n" + "="*50)
    print("TEST: Concurrent Ratings on Same User")
    print("="*50)

    host_id = MEMBER_IDS[0]
    print(host_id)
    passengers = MEMBER_IDS[1:4]  # 3 passengers will rate the host

    # Step 1: Host creates a ride
    start_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    r = requests.post(
        f"{BASE_URL}/rides",
        json={
            "AdminID": host_id,
            "Source": "Gate",
            "Destination": "Hostel",
            "StartTime": start_time,
            "AvailableSeats": 3,
            "VehicleType": "Car",
            "FemaleOnly": False,
            "EstimatedTime": 10
        },
        headers={"X-Test-User-ID": str(host_id)}
    )
    ride_id = r.json()["RideID"]
    print(f"Ride created: {ride_id}")

    # Step 2: All passengers send booking requests
    req_ids = []
    for uid in passengers:
        r = requests.post(
            f"{BASE_URL}/booking-requests",
            json={"RideID": ride_id},
            headers={"X-Test-User-ID": str(uid)}
        )
        req_ids.append(r.json()["RequestID"])
    print(f"Booking requests created: {req_ids}")

    # Step 3: Host approves all passengers
    for req_id in req_ids:
        requests.patch(
            f"{BASE_URL}/booking-requests/{req_id}",
            json={"RequestStatus": "APPROVED"},
            headers={"X-Test-User-ID": str(host_id)}
        )
    print("All passengers approved")

    # Step 4: Host marks ride as completed
    r = requests.patch(
        f"{BASE_URL}/rides/{ride_id}/status",
        json={"status": "COMPLETED", "platform": "Ola", "price": 100},
        headers={"X-Test-User-ID": str(host_id)}
    )
    print(f"Ride completed: {r.json()}")

    # Step 5: Check host's stat BEFORE ratings
    with engine.connect() as conn:
        row = conn.execute(text(
            f"SELECT AverageRating, NumberOfRatings FROM MemberStats WHERE MemberID = {host_id}"
        )).fetchone()
        if row:
            before_avg, before_count = float(row[0]), int(row[1])  # ← cast here
        else:
            before_avg, before_count = 0.0, 0
    print(f"\nBefore ratings → AverageRating: {before_avg}, NumberOfRatings: {before_count}")

    # Step 6: All 3 passengers rate the host SIMULTANEOUSLY
    ratings = [5.0, 3.0, 4.0]  # known values so we can verify the math
    expected_avg = round(
        (before_avg * before_count + sum(ratings)) / (before_count + len(ratings)), 4
    )
    print(f"Ratings to submit: {ratings}")
    print(f"Expected average after: {expected_avg}")

    barrier = threading.Barrier(len(passengers))
    results = {}

    def submit_rating(user_id, rating):
        barrier.wait()  # All fire at the same time
        r = requests.post(
            f"{BASE_URL}/ratings",
            json={
                "RideID": ride_id,
                "ReceiverMemberID": host_id,
                "Rating": rating,
                "RatingComment": f"Rated by {user_id}"
            },
            headers={"X-Test-User-ID": str(user_id)}
        )
        results[user_id] = (r.status_code, r.json())

    threads = [
        threading.Thread(target=submit_rating, args=(uid, rating))
        for uid, rating in zip(passengers, ratings)
    ]
    for t in threads: t.start()
    for t in threads: t.join()

    for uid, (status, body) in results.items():
        print(f"User {uid}: {status} - {body}")

    # Step 7: Verify DB state
    with engine.connect() as conn:
        row = conn.execute(text(
            f"SELECT AverageRating, NumberOfRatings FROM MemberStats WHERE MemberID = {host_id}"
        )).fetchone()
        actual_avg = round(float(row[0]), 4)  # ← cast here too
        actual_count = int(row[1])

    print(f"\nAfter ratings → AverageRating: {actual_avg}, NumberOfRatings: {actual_count}")
    print(f"Expected       → AverageRating: {expected_avg}, NumberOfRatings: {before_count + len(ratings)}")

    if actual_count == before_count + len(ratings) and actual_avg == expected_avg:
        print("✅ PASSED: Average and count are correct")
    else:
        if actual_count != before_count + len(ratings):
            print(f"🚨 RACE CONDITION: Expected {before_count + len(ratings)} ratings, got {actual_count} — a rating was lost!")
        if actual_avg != expected_avg:
            print(f"🚨 RACE CONDITION: Average is wrong — concurrent writes overwrote each other!")

if __name__ == "__main__":
    test_concurrent_ratings()