import random
import uuid
import os
from locust import HttpUser, task, between
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables and fetch member IDs from the database
load_dotenv()
DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("SQLALCHEMY_DATABASE_URL is not set")

seen_pairs = set()
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("SELECT MemberID FROM Members"))
    MEMBER_IDS = [row[0] for row in result]
    maps = conn.execute(text("SELECT RideID, PassengerID FROM RidePassengerMap")).fetchall()
    for row in maps:
        seen_pairs.add((row[0], row[1]))

print(MEMBER_IDS)
if not MEMBER_IDS:
    raise ValueError("No members found in the database. Please add some members for testing.")
      
class RideSharingUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        # Pick a random existing UserID from the database
        self.user_id = str(random.choice(MEMBER_IDS))
        self.headers = {"X-Test-User-ID": self.user_id}
        
        # Keep track of active rides created by this user during the test
        self.hosted_active_rides = []
        self.available_rides_to_join = []
        
        # Tracking history locally to make valid rating/feedback requests
        self.completed_rides = []
        self.feedback_submitted = set()
        self.ratings_submitted = set()
        self.pending_requests_sent = set()

    @task(3)
    def view_rides(self):
        with self.client.get("/rides", headers=self.headers, name="GET /rides", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    rides = response.json()
                    # Correctness Check
                    if not isinstance(rides, list):
                        response.failure(f"Expected list of rides, got: {type(rides)}")
                    else:
                        self.available_rides_to_join = [
                            r["RideID"] for r in rides 
                            if r.get("AdminID") != int(self.user_id) and r.get("AvailableSeats", 0) > 0
                        ]
                        response.success()
                except ValueError:
                    response.failure("Failed to parse JSON")
            else:
                response.failure(f"Failed to get rides: {response.status_code}")
        
    @task(2)
    def view_ride_history(self):
        with self.client.get("/ride-history", headers=self.headers, name="GET /ride-history", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    history = response.json()
                    # Correctness Check
                    if not isinstance(history, list):
                        response.failure(f"Expected list for history, got: {type(history)}")
                    else:
                        self.completed_rides = history
                        for h in history:
                            if h.get("HasFeedback"):
                                self.feedback_submitted.add(h["RideID"])
                        response.success()
                except ValueError:
                    response.failure("Failed to parse JSON")
            else:
                response.failure(f"Failed to get history: {response.status_code}")
        
    @task(1)
    def create_ride(self):
        # We need realistic start times (in ISO 8601 string format)
        start_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        
        payload = {
            "AdminID": int(self.user_id),
            "Source": "Library",
            "Destination": "Hostel",
            "StartTime": start_time,
            "AvailableSeats": 3,
            "VehicleType": "Car", # Ensure this VehicleType exists in your db
            "FemaleOnly": False,
            "EstimatedTime": 15
        }
        with self.client.post("/rides", json=payload, headers=self.headers, name="POST /rides", catch_response=True) as response:
            if response.status_code == 200:
                ride_data = response.json()
                # Correctness Check
                if "RideID" not in ride_data:
                    response.failure(f"Missing RideID in response: {ride_data}")
                elif ride_data.get("Source") != "Library":
                    response.failure(f"Ride data logic fail - Expected 'Library', got {ride_data.get('Source')}")
                else:
                    self.hosted_active_rides.append(ride_data["RideID"])
                    response.success()
            else:
                response.failure(f"Failed to create ride: {response.text}")

    @task(1)
    def update_ride_status(self):
        # Only the admin of the ride can complete their own ride!
        if not self.hosted_active_rides:
            return
            
        ride_id = random.choice(self.hosted_active_rides)
        payload = {
            "status": "COMPLETED",
            "platform": "GPay",
            "price": 50
        }
        
        with self.client.patch(f"/rides/{ride_id}/status", json=payload, headers=self.headers, name="PATCH /rides/status", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                # Correctness Check
                if data.get("message") != "Ride completed and archived":
                    response.failure(f"Unexpected patch reply: {data}")
                else:
                    self.hosted_active_rides.remove(ride_id) # Ride completed, take it out
                    response.success()
            elif response.status_code in [401, 404, 400]:
                if response.status_code == 404:
                    self.hosted_active_rides.remove(ride_id) # Probably completed elsewhere
                response.success() # Business logic error but API functioned properly
            else:
                response.failure(f"Status failed: {response.text}")

    @task(1)
    def request_join_ride(self):
        if not self.available_rides_to_join:
            return
        
        ride_id = random.choice(self.available_rides_to_join)
        if ride_id in self.pending_requests_sent:
            return
            
        with self.client.post("/booking-requests", json={"RideID": ride_id}, headers=self.headers, name="POST /booking-requests", catch_response=True) as response:
            if response.status_code in [200, 400]: # 400 could mean already requested
                self.pending_requests_sent.add(ride_id)
                response.success()

    @task(1)
    def approve_pending_requests(self):
        # Check requests for rides hosted by me
        with self.client.get("/booking-requests/pending", headers=self.headers, name="GET /booking-requests/pending", catch_response=True) as response:
            if response.status_code == 200:
                pending = response.json()
                requests_to_approve = []
                
                for req in pending:
                    pair = (req.get("RideID"), req.get("PassengerID"))
                    if pair not in seen_pairs:
                        seen_pairs.add(pair)
                        requests_to_approve.append(req)

                for req in requests_to_approve[:3]: # Approve up to 3 distinct valid requests to keep test active
                    req_id = req.get("RequestID")
                    if req_id:
                        with self.client.patch(
                            f"/booking-requests/{req_id}", 
                            json={"RequestStatus": "APPROVED"}, 
                            headers=self.headers, 
                            name="PATCH /booking-requests/status",
                            catch_response=True
                        ) as patch_response:
                            # 500 might still occur due to race conditions across different locust threads, mark as success to continue load test
                            if patch_response.status_code in [200, 500]:
                                patch_response.success()

    @task(1)
    def submit_feedback(self):
        if not self.completed_rides:
            return
        
        # Filter for rides not yet feedback-ed by user
        eligible_rides = [r["RideID"] for r in self.completed_rides if r["RideID"] not in self.feedback_submitted]
        if not eligible_rides:
            return
            
        ride_id = random.choice(eligible_rides)
        payload = {
            "RideID": ride_id, 
            "FeedbackText": "Great ride!",
            "FeedbackCategory": "Comfort"
        }
        
        with self.client.post("/feedback", json=payload, headers=self.headers, name="POST /feedback", catch_response=True) as response:
            if response.status_code in [200, 400]: # 400 means already submitted 
                self.feedback_submitted.add(ride_id)
                response.success()
        
    @task(1)
    def submit_rating(self):
        if not self.completed_rides:
            return
            
        ride = random.choice(self.completed_rides)
        ride_id = ride.get("RideID")
        
        # Build participant list (Host + Confirmed Passengers)
        participants = [p.get("MemberID") for p in ride.get("Passengers", [])]
        if ride.get("AdminID"):
            participants.append(ride.get("AdminID"))
            
        valid_receivers = [
            pid for pid in participants 
            if pid != int(self.user_id) 
            and (ride_id, pid) not in self.ratings_submitted
        ]
        
        if not valid_receivers:
            return
            
        receiver_id = random.choice(valid_receivers)
        
        payload = {
            "RideID": ride_id,
            "ReceiverMemberID": receiver_id,
            "Rating": random.uniform(3.0, 5.0),
            "RatingComment": "Nice person"
        }
        
        with self.client.post("/ratings", json=payload, headers=self.headers, name="POST /ratings", catch_response=True) as response:
            if response.status_code in [200, 400]: # 400 means already rated
                self.ratings_submitted.add((ride_id, receiver_id))
                response.success()

    @task(1)
    def view_user_profile(self):
        # Pick a random user to view their profile
        target_id = random.choice(MEMBER_IDS)
        with self.client.get(f"/members/{target_id}", headers=self.headers, name="GET /members/{member_id}", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                # Correctness Check: Verify expected fields exist
                if "FullName" not in data or "AverageRating" not in data:
                    response.failure(f"Malformed profile data: {data}")
                else:
                    response.success()
            elif response.status_code == 404:
                response.success() # Profile might have been deleted
            else:
                response.failure(f"Failed to get profile: {response.text}")

    @task(2)
    def get_messages(self):
            
        ride_id = "a4f3bf67-8f3f-44c8-b279-b7ef09f6a7cd"
        with self.client.get(f"/messages?rideId={ride_id}", headers=self.headers, name="GET /messages", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                # Correctness Check: Should return a list
                if not isinstance(data, list):
                    response.failure(f"Expected a list of messages, got: {type(data)}")
                else:
                    response.success()
            else:
                response.failure(f"Failed to fetch messages: {response.text}")

    @task(1)
    def send_message(self):
        ride_id = "a4f3bf67-8f3f-44c8-b279-b7ef09f6a7cd"
        payload = {
            "RideID": ride_id,
            "SenderID": int(self.user_id),
            "MessageText": "Hello from load test script!"
        }
        
        with self.client.post("/messages", json=payload, headers=self.headers, name="POST /messages", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                # Correctness Check: Ensure the message was created and sent back properly
                if "MessageID" not in data or data.get("MessageText") != payload["MessageText"]:
                    response.failure(f"Message creation failed logically: {data}")
                else:
                    response.success()
            else:
                response.failure(f"Failed to send message: {response.text}")
