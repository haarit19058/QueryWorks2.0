import threading
import requests
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")
engine = create_engine(DATABASE_URL)
BASE_URL = "http://localhost:8000"

with engine.connect() as conn:
    result = conn.execute(text("SELECT MemberID FROM Members"))
    MEMBER_IDS = [row[0] for row in result]

# ─────────────────────────────────────────────
# TEST 1: Multiple users fetching rides simultaneously
# Verifies: Read isolation — all users get same consistent data
# ─────────────────────────────────────────────
def test_concurrent_reads():
    print("\n" + "="*50)
    print("TEST 1: Concurrent Read Access")
    print("="*50)
    print("How it checks success: It fetches ALL rides concurrently across different user sessions. It verifies that despite hitting the database simultaneously, every thread gets the EXACT SAME count of rides, proving read isolation is preserved.")

    results = {}

    def fetch_rides(user_id):
        r = requests.get(
            f"{BASE_URL}/rides",
            headers={"X-Test-User-ID": str(user_id)}
        )
        results[user_id] = len(r.json())

    threads = [
        threading.Thread(target=fetch_rides, args=(uid,))
        for uid in MEMBER_IDS[:5]
    ]
    for t in threads: t.start()
    for t in threads: t.join()

    print(f"Rides seen by each user: {results}")

    # All users should see the same number of rides
    unique_counts = set(results.values())
    if len(unique_counts) == 1:
        print("✅ PASSED: All users see consistent ride data")
    else:
        print("🚨 FAILED: Users are seeing different data — isolation issue!")


# ─────────────────────────────────────────────
# TEST 2: Multiple users booking the SAME ride simultaneously
# Verifies: Users don't interfere — only one request per user gets created
# ─────────────────────────────────────────────
def test_concurrent_booking_requests(ride_id):
    print("\n" + "="*50)
    print("TEST 2: Concurrent Booking Requests (Different Users, Same Ride)")
    print("="*50)
    print("How it checks success: 5 distinct users attempt to book the very SAME ride at the exact same millisecond. It queries the DB immediately after to confirm that exactly 1 booking request is created per user, ensuring simultaneous writes don't override or duplicate each other's data.")

    passengers = MEMBER_IDS[1:6]  # 5 users try to book same ride
    results = {}
    barrier = threading.Barrier(len(passengers))

    def send_booking(user_id):
        barrier.wait()  # All fire at the same time
        r = requests.post(
            f"{BASE_URL}/booking-requests",
            json={"RideID": ride_id},
            headers={"X-Test-User-ID": str(user_id)}
        )
        results[user_id] = r.status_code

    threads = [
        threading.Thread(target=send_booking, args=(uid,))
        for uid in passengers
    ]
    for t in threads: t.start()
    for t in threads: t.join()

    print(f"Booking response codes: {results}")

    # Verify in DB — each user should have exactly 1 booking request
    with engine.connect() as conn:
        for user_id in passengers:
            count = conn.execute(text(
                f"SELECT COUNT(*) FROM BookingRequests WHERE RideID = '{ride_id}' AND PassengerID = {user_id}"
            )).fetchone()[0]

            if count == 1:
                print(f"✅ User {user_id}: Exactly 1 booking request created")
            elif count == 0:
                print(f"⚠️  User {user_id}: No booking request found")
            else:
                print(f"🚨 User {user_id}: DUPLICATE bookings created ({count}) — isolation failure!")


# ─────────────────────────────────────────────
# TEST 3: Multiple users sending messages to same ride simultaneously
# Verifies: No messages lost, no duplicates, users don't overwrite each other
# ─────────────────────────────────────────────
def test_concurrent_messages(ride_id):
    print("\n" + "="*50)
    print("TEST 3: Concurrent Messaging (Same Ride Chat)")
    print("="*50)
    print("How it checks success: Multiple users post messages to the same ride concurrently. It verifies the DB to ensure every single message is saved perfectly intact without dropping any or mixing sender IDs.")

    users = MEMBER_IDS[:4]
    barrier = threading.Barrier(len(users))
    results = {}

    def send_message(user_id):
        barrier.wait()
        r = requests.post(
            f"{BASE_URL}/messages",
            json={
                "RideID": ride_id,
                "SenderID": user_id,
                "MessageText": f"Hello from user {user_id}"
            },
            headers={"X-Test-User-ID": str(user_id)}
        )
        results[user_id] = r.status_code

    threads = [
        threading.Thread(target=send_message, args=(uid,))
        for uid in users
    ]
    for t in threads: t.start()
    for t in threads: t.join()

    print(f"Message send response codes: {results}")

    # Verify: All messages were stored, each attributed to correct sender
    with engine.connect() as conn:
        for user_id in users:
            count = conn.execute(text(
                f"SELECT COUNT(*) FROM MessageHistory WHERE RideID = '{ride_id}' AND SenderID = {user_id}"
            )).fetchone()[0]

            if count == 1:
                print(f"✅ User {user_id}: Message correctly stored")
            else:
                print(f"🚨 User {user_id}: Expected 1 message, found {count} — data integrity issue!")


# ─────────────────────────────────────────────
# TEST 4: Two users trying to create rides at the same time
# Verifies: Each user gets their own independent ride, no cross-contamination
# ─────────────────────────────────────────────
def test_concurrent_ride_creation():
    print("\n" + "="*50)
    print("TEST 4: Concurrent Ride Creation (Different Users)")
    print("="*50)
    print("How it checks success: Multiple valid users create new rides concurrently. It validates the API responses to ensure each individual ride is returned perfectly tied to only that admin's ID, avoiding ID mismatches.")

    from datetime import datetime, timedelta, timezone
    users = MEMBER_IDS[:3]
    barrier = threading.Barrier(len(users))
    results = {}

    def create_ride(user_id):
        barrier.wait()
        start_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        r = requests.post(
            f"{BASE_URL}/rides",
            json={
                "AdminID": user_id,
                "Source": f"Point A ({user_id})",
                "Destination": f"Point B ({user_id})",
                "StartTime": start_time,
                "AvailableSeats": 2,
                "VehicleType": "Car",
                "FemaleOnly": False,
                "EstimatedTime": 20
            },
            headers={"X-Test-User-ID": str(user_id)}
        )
        results[user_id] = r.json()

    threads = [
        threading.Thread(target=create_ride, args=(uid,))
        for uid in users
    ]
    for t in threads: t.start()
    for t in threads: t.join()

    # Verify: Each ride has the correct AdminID — no cross-contamination
    all_passed = True
    for user_id, ride in results.items():
        if ride.get("AdminID") == user_id:
            print(f"✅ User {user_id}: Ride created with correct AdminID")
        else:
            print(f"🚨 User {user_id}: Ride has wrong AdminID {ride.get('AdminID')} — data contamination!")
            all_passed = False

    if all_passed:
        print("✅ PASSED: All rides correctly isolated to their respective admins")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Create a shared ride for tests 2 & 3
    from datetime import datetime, timedelta, timezone
    start_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    r = requests.post(
        f"{BASE_URL}/rides",
        json={
            "AdminID": MEMBER_IDS[0],
            "Source": "Gate", "Destination": "Hostel",
            "StartTime": start_time,
            "AvailableSeats": 3,
            "VehicleType": "Car",
            "FemaleOnly": False,
            "EstimatedTime": 10
        },
        headers={"X-Test-User-ID": str(MEMBER_IDS[0])}
    )
    shared_ride_id = r.json()["RideID"]
    print(f"Shared ride created: {shared_ride_id}")

    test_concurrent_reads()
    test_concurrent_booking_requests(shared_ride_id)
    test_concurrent_messages(shared_ride_id)
    test_concurrent_ride_creation()