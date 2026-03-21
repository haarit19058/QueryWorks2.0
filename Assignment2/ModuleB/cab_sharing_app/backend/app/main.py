import requests as http_requests # Add this to your imports at the top
from fastapi import FastAPI, Depends, HTTPException, Response, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker, joinedload
from sqlalchemy import create_engine
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel
import jwt
import json
from datetime import datetime, timedelta, timezone

from models import * #Base, Member, ActiveRide, BookingRequest, MessageHistory, MemberStat
from typing import Any

from dotenv import load_dotenv 
import logging
from logging.handlers import RotatingFileHandler
import time
import os
load_dotenv()

DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL") # Update to your MySQL connection string
GOOGLE_CLIENT_ID = os.environ.get("CLIENT_ID")
JWT_SECRET = os.environ.get("JWT_SECRET_KEY", "fallback-secret-key")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
ALGORITHM = "HS256"
ADMIN_FILE = "admin.json"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
LOG_FILE_PATH = os.path.join(PARENT_DIR, "logs.log")

log_formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 3. Setup the File Handler (Rotates at 5MB, keeps 3 backups)
file_handler = RotatingFileHandler(
    filename=LOG_FILE_PATH,
    maxBytes=5 * 1024 * 1024,  # 5 MB max file size
    backupCount=3              # Keep up to 3 old log files
)
file_handler.setFormatter(log_formatter)

# 4. Setup Console Handler (So you still see logs in your terminal)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# 5. Initialize the root logger
logger = logging.getLogger("ride_sharing_app")
logger.setLevel(logging.INFO) # Change to DEBUG for more verbosity
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Override FastAPI and Uvicorn default loggers to use our file handler too
logging.getLogger("uvicorn.access").handlers = [console_handler, file_handler]
logging.getLogger("fastapi").handlers = [console_handler, file_handler]



# --- Database Setup ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Config ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:3000","http://127.0.0.1:3000","http://10.7.59.24:3000"], # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Logging Middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.2f}ms"
    )
    return response

# --- Pydantic Schemas ---
class GoogleLoginData(BaseModel):
    code: str

class SignupData(BaseModel):
    google_sub: str
    FullName: str
    Email: str
    ProfileImageURL: str
    Programme: str
    Branch: str | None = None
    BatchYear: int
    ContactNumber: str
    Gender: str
    Age: int | None = None

class RideCreateData(BaseModel):
    AdminID: int
    Source: str
    Destination: str
    StartTime: str
    AvailableSeats: int
    VehicleType: str
    FemaleOnly: bool
    EstimatedTime: int

class RequestJoinData(BaseModel):
    RideID: str

class UpdateRequestData(BaseModel):
    RequestStatus: str

class MessageCreateData(BaseModel):
    RideID: str
    SenderID: int
    MessageText: str

class UpdateRideStatusData(BaseModel):
    status: str

# --- Auth Middleware ---
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        logger.warning("Authentication failed: No session token found.")
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        
        # FIX: Cast the string subject back to an integer for the database
        member_id = int(payload.get("sub")) 
        
        logger.info(f"* DB SELECT: Checking Member table for MemberID: {member_id}")
        user = db.query(Member).filter(Member.MemberID == member_id).first()
        if not user:
            logger.warning(f"Authentication failed: User ID {member_id} not found in database.")
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        logger.warning("Authentication failed: Session expired.")
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.PyJWTError as e:
        # print(f"JWT DECODE ERROR: {e}") 
        logger.error(f"JWT DECODE ERROR: {e}")
        raise HTTPException(status_code=401, detail="Invalid session")

def create_cookie(response: Response, member_id: int):
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    # FIX: Cast member_id to a string ("sub" must be a string)
    token = jwt.encode({"sub": str(member_id), "exp": expire}, JWT_SECRET, algorithm=ALGORITHM)
    
    response.set_cookie(
        key="session_token", 
        value=token, 
        httponly=True, 
        max_age=604800,
        path="/", 
        samesite="lax",    
        secure=False       
    )
@app.post("")
def home():
    return {"message": "Welcome to home page!"}

@app.post("/auth/login") # (Or /api/auth/login depending on how you fixed the 404s)
def login(data: GoogleLoginData, response: Response, db: Session = Depends(get_db)):
    # 1. Exchange the Authorization Code for an ID Token
    token_url = "https://oauth2.googleapis.com/token"
    token_payload = {
        "code": data.code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": "postmessage", # This is required when using @react-oauth/google's auth-code flow
        "grant_type": "authorization_code"
    }
    
    token_res = http_requests.post(token_url, data=token_payload)
    
    if token_res.status_code != 200:
        # print("Google Token Exchange Error:", token_res.json()) # Helpful for debugging
        logger.warning(f"Google Token Exchange Failed. Response: {token_res.json()}")
        raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
        
    token_data = token_res.json()
    extracted_id_token = token_data.get("id_token")

    # 2. Verify the ID Token now that we have it
    try:
        from google.auth.transport import requests as google_requests
        idinfo = id_token.verify_oauth2_token(extracted_id_token, google_requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo['email']
        
        if not email.endswith('@iitgn.ac.in'):
            logger.warning(f"Failed login attempt: Unauthorized email domain ({email})")
            raise HTTPException(status_code=403, detail="Only IITGN emails allowed")

        logger.info(f"* DB SELECT: Checking Member table for Email: {email}")
        user = db.query(Member).filter(Member.Email == email).first()
        
        if user:
            logger.info(f"User logged in successfully: {email} (ID: {user.MemberID})")
            create_cookie(response, user.MemberID)
            return {"isNewUser": False, "user": user}
        else:
            logger.info(f"New user registration initiated for: {email}")
            return {
                "isNewUser": True,
                "email": email,
                "name": idinfo.get("name"),
                "picture": idinfo.get("picture"),
                "google_sub": idinfo["sub"]
            }
    except ValueError as e:
        logger.error(f"Invalid Google token validation error: {e}")
        raise HTTPException(status_code=400, detail="Invalid Google token")

@app.post("/auth/signup")
def signup(data: SignupData, response: Response, db: Session = Depends(get_db)):
    new_user = Member(
        GoogleSub=data.google_sub, FullName=data.FullName, Email=data.Email,
        ProfileImageURL=data.ProfileImageURL, Programme=data.Programme,
        Branch=data.Branch, BatchYear=data.BatchYear, ContactNumber=data.ContactNumber,
        Gender=data.Gender, Age=data.Age
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"* DB INSERT: Added new Member into database (Email: {data.Email}, ID: {new_user.MemberID})")
    create_cookie(response, new_user.MemberID)
    logger.info(f"New user signed up successfully: {new_user.Email} (ID: {new_user.MemberID})")
    return {"user": new_user}

@app.get("/auth/me")
def get_me(user: Member = Depends(get_current_user)):
    return user

@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie("session_token")
    # logger.info(f"User logged out: {user.Email} (ID: {user.MemberID})")
    return {"message": "Logged out"}

# --- Routes: Rides ---
@app.get("/rides")
def get_rides(db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
# def get_rides(db: Session = Depends(get_db)):
    # print(current_user)
    # logger.debug(f"Fetching all active rides for user ID: {current_user.MemberID}")
    
    logger.info("* DB SELECT: Fetching all ActiveRides")
    rides = db.query(ActiveRide).all()
    result = []
    
    for ride in rides:
        # Get host info
        logger.info(f"* DB SELECT: Fetching Host Member with MemberID: {ride.AdminID}")
        host = db.query(Member).filter(Member.MemberID == ride.AdminID).first()
        
        # Get approved passengers
        logger.info(f"* DB SELECT: Fetching APPROVED BookingRequests for RideID: {ride.RideID}")
        # approved_reqs = db.query(BookingRequest).filter(
        #     BookingRequest.RideID == ride.RideID, 
        #     BookingRequest.RequestStatus == "APPROVED"
        # ).all()
        
        # passengers = []
        # for req in approved_reqs:
        #     logger.info(f"* DB SELECT: Fetching Passenger Member with MemberID: {req.PassengerID}")
        #     p = db.query(Member).filter(Member.MemberID == req.PassengerID).first()
        #     if p:
        #         passengers.append({"MemberID": p.MemberID, "FullName": p.FullName})
        rides = db.query(ActiveRide).options(
            joinedload(ActiveRide.admin),
            joinedload(ActiveRide.requests).joinedload(BookingRequest.passenger)
        ).filter(ActiveRide.Status == "ACTIVE").all()
    
    result = []
    for ride in rides:
        # Passengers are now already in memory thanks to joinedload
        passengers = [
            {"MemberID": req.passenger.MemberID, "FullName": req.passenger.FullName}
            for req in ride.requests if req.RequestStatus == "APPROVED"
        ]
        
        result.append({
            "RideID": ride.RideID,
            "AdminID": ride.AdminID,
            "HostName": host.FullName if host else "Unknown",
            "ProfileImageURL": host.ProfileImageURL if host else "",
            "AvailableSeats": ride.AvailableSeats,
            "PassengerCount": ride.PassengerCount,
            "Source": ride.Source,
            "Destination": ride.Destination,
            "VehicleType": ride.VehicleType,
            "StartTime": ride.StartTime.isoformat(),
            "EstimatedTime": ride.EstimatedTime,
            "FemaleOnly": ride.FemaleOnly,
            "status": ride.Status,
            "Passengers": passengers
        })
        
    return result

@app.post("/rides")
def create_ride(data: RideCreateData, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    new_ride = ActiveRide(
        AdminID=user.MemberID, Source=data.Source, Destination=data.Destination,
        StartTime=datetime.fromisoformat(data.StartTime), AvailableSeats=data.AvailableSeats,
        PassengerCount=1, VehicleType=data.VehicleType, FemaleOnly=data.FemaleOnly,
        EstimatedTime=data.EstimatedTime
    )
    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    logger.info(f"* DB INSERT: Added new ActiveRide (RideID: {new_ride.RideID}) by AdminID: {user.MemberID}")
    logger.info(f"New ride created: RideID {new_ride.RideID} by UserID {user.MemberID} ({data.Source} to {data.Destination})")
    return new_ride

@app.patch("/rides/{ride_id}/status")
def update_ride_status(ride_id: str, data: UpdateRideStatusData, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    logger.info(f"* DB SELECT: Fetching ActiveRide with RideID: {ride_id} for AdminID: {user.MemberID}")
    ride = db.query(ActiveRide).filter(ActiveRide.RideID == ride_id, ActiveRide.AdminID == user.MemberID).first()
    if not ride:
        logger.warning(f"Failed status update attempt: Ride {ride_id} not found or unauthorized by UserID {user.MemberID}")
        raise HTTPException(status_code=404, detail="Ride not found or unauthorized")
    old_status = ride.Status
    ride.Status = data.status
    db.commit()
    logger.info(f"* DB UPDATE: Status updated for ActiveRide (RideID: {ride_id}) to {data.status}")
    logger.info(f"Ride status updated: RideID {ride_id} from {old_status} to {data.status} by UserID {user.MemberID}")
    return {"message": "Status updated"}

# --- Routes: Bookings ---
# This api is for the AvailableRides page to show the user correct UI
@app.get("/booking-requests")
def get_bookings(db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    # The frontend fetches requests for the current user
    logger.info(f"* DB SELECT: Fetching BookingRequests for PassengerID: {user.MemberID}")
    requests = db.query(BookingRequest).filter(BookingRequest.PassengerID == user.MemberID).all()
    return requests

# My booking requests (send by by)
@app.post("/booking-requests")
def request_join(data: RequestJoinData, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    new_req = BookingRequest(RideID=data.RideID, PassengerID=user.MemberID)
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    logger.info(f"* DB INSERT: Added new BookingRequest (RequestID: {new_req.RequestID}) for RideID: {data.RideID}")
    logger.info(f"New booking request: RequestID {new_req.RequestID} by UserID {user.MemberID} for RideID {data.RideID}")
    return new_req

# Booking requests sent to admin (sent to me)
@app.get("/booking-requests/pending")
def get_pending_requests(
    db: Session = Depends(get_db),
    user: Member = Depends(get_current_user)
):
    logger.info(f"* DB SELECT: Fetching PENDING BookingRequests joined with ActiveRides for AdminID: {user.MemberID}")
    results = (
        db.query(BookingRequest)
        .join(ActiveRide, BookingRequest.RideID == ActiveRide.RideID)
        .filter(
            ActiveRide.AdminID == user.MemberID,   # YOU are admin
            BookingRequest.RequestStatus == "PENDING"
        )
        .all()
    )
    return results

@app.patch("/booking-requests/{request_id}")
def update_booking(request_id: int, data: UpdateRequestData, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    logger.info(f"* DB SELECT: Fetching BookingRequest with RequestID: {request_id}")
    req = db.query(BookingRequest).filter(BookingRequest.RequestID == request_id).first()
    if not req:
        logger.warning(f"Failed booking update: RequestID {request_id} not found.")
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Optional: Verify current_user is the Admin of the ride
    old_status = req.RequestStatus
    req.RequestStatus = data.RequestStatus
    
    if data.RequestStatus == "APPROVED":
        logger.info(f"* DB SELECT: Fetching ActiveRide with RideID: {req.RideID} to decrement seats")
        ride = db.query(ActiveRide).filter(ActiveRide.RideID == req.RideID).first()
        if ride and ride.AvailableSeats > 0:
            ride.AvailableSeats -= 1
            ride.PassengerCount += 1
            logger.info(f"Seat decremented for RideID {req.RideID}. Seats left: {ride.AvailableSeats}")
            
    db.commit()
    logger.info(f"* DB UPDATE: Updated BookingRequest RequestStatus to {data.RequestStatus} (and optionally ActiveRide seats) for RequestID: {request_id}")
    logger.info(f"Booking status updated: RequestID {request_id} from {old_status} to {data.RequestStatus} by UserID {user.MemberID}")
    return {"message": "Request updated"}

# --- Routes: Messages ---
@app.get("/messages")
def get_messages(rideId: str, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    logger.info(f"* DB SELECT: Fetching MessageHistory for RideID: {rideId}")
    messages = db.query(MessageHistory).filter(MessageHistory.RideID == rideId).order_by(MessageHistory.Timestamp.asc()).all()
    
    result = []
    for msg in messages:
        logger.info(f"* DB SELECT: Fetching Sender Member with MemberID: {msg.SenderID}")
        sender = db.query(Member).filter(Member.MemberID == msg.SenderID).first()
        result.append({
            "MessageID": msg.MessageID,
            "RideID": msg.RideID,
            "SenderID": msg.SenderID,
            "SenderName": sender.FullName if sender else "Unknown",
            "SenderAvatar": sender.ProfileImageURL if sender else "",
            "MessageText": msg.MessageText,
            "Timestamp": msg.Timestamp.isoformat(),
            "IsRead": msg.IsRead
        })
    return result

@app.post("/messages")
def send_message(data: MessageCreateData, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    new_msg = MessageHistory(RideID=data.RideID, SenderID=user.MemberID, MessageText=data.MessageText)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    logger.info(f"* DB INSERT: Added new MessageHistory (MessageID: {new_msg.MessageID}) for RideID: {data.RideID}")
    logger.debug(f"Message sent in RideID {data.RideID} by UserID {user.MemberID}")
    return {
        "MessageID": new_msg.MessageID,
        "RideID": new_msg.RideID,
        "SenderID": new_msg.SenderID,
        "SenderName": user.FullName,
        "SenderAvatar": user.ProfileImageURL,
        "MessageText": new_msg.MessageText,
        "Timestamp": new_msg.Timestamp.isoformat(),
        "IsRead": new_msg.IsRead
    }


@app.get("/api/members/{member_id}")
def get_user_profile(member_id: int, db: Session = Depends(get_db)) -> Any:
    """
    Fetch a user's profile details along with their ride statistics.
    """
    # Query both Member and MemberStat tables using an outer join
    logger.info(f"* DB SELECT: Fetching Member and MemberStat details for MemberID: {member_id}")
    result = (
        db.query(Member, MemberStat)
        .outerjoin(MemberStat, Member.MemberID == MemberStat.MemberID)
        .filter(Member.MemberID == member_id)
        .first()
    )

    # If no member is found, return a 404
    if not result:
        logger.warning(f"Profile lookup failed: UserID {member_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found."
        )

    member, stats = result
    return {
        "MemberID": member.MemberID,
        "FullName": member.FullName,
        "ProfileImageURL": member.ProfileImageURL,
        "Programme": member.Programme,
        "Branch": member.Branch,
        "BatchYear": member.BatchYear,
        "Age": member.Age,
        "Gender": member.Gender,
        
        "AverageRating": stats.AverageRating if stats else 0.0,
        "TotalRidesTaken": stats.TotalRidesTaken if stats else 0,
        "TotalRidesHosted": stats.TotalRidesHosted if stats else 0,
        "NumberOfRatings": stats.NumberOfRatings if stats else 0,
    }


# ------------------ HELPERS ------------------
def read_admin_file():
    try:
        with open(ADMIN_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Admin file {ADMIN_FILE} not found.")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Admin file {ADMIN_FILE} contains invalid JSON.")
        return {}

def write_admin_file(data):
    try:
        with open(ADMIN_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to write to admin file: {e}")

def is_admin(member_id: int) -> bool:
    data = read_admin_file()
    return member_id in data.get("Admin_Member_Ids", [])

def verify_admin(member_id: int):
    if not is_admin(member_id):
        logger.warning(f"Unauthorized admin action blocked for UserID: {member_id}")
        raise HTTPException(status_code=403, detail="Not an admin")


# ------------------ PUBLIC CHECK ------------------
@app.get("/api/is-admin")
def check_admin(member_id: int):
    return {"is_admin": is_admin(member_id)}


# ------------------ ADMIN APIs ------------------

# 1. GET current admins
@app.get("/api/admin/current-admins")
def get_current_admins(member_id: int, db: Session = Depends(get_db)):
    verify_admin(member_id)

    data = read_admin_file()
    ids = data.get("Admin_Member_Ids", [])

    logger.info(f"* DB SELECT: Fetching Members associated with Admin IDs")
    admins = db.query(Member).filter(Member.MemberID.in_(ids)).all()

    return [
        {"MemberID": a.MemberID, "FullName": a.FullName, "Email": a.Email}
        for a in admins
    ]


# 2. POST add admin
@app.post("/api/admin/add-admin")
def add_admin(member_id: int, email: str, db: Session = Depends(get_db)):
    verify_admin(member_id)

    logger.info(f"* DB SELECT: Fetching Member with Email: {email} to add as admin")
    member = db.query(Member).filter(Member.Email == email).first()
    if not member:
        logger.warning(f"Admin addition failed: Email {email} not found in database.")
        raise HTTPException(404, "Member not found")

    data = read_admin_file()

    if member.MemberID in data["Admin_Member_Ids"]:
        return {"msg": "Already admin"}

    data["Admin_Member_Ids"].append(member.MemberID)
    data["Admin_Emails"].append(email)

    write_admin_file(data)
    logger.info(f"System Admin {member_id} granted admin privileges to {email} (ID: {member.MemberID})")
    return {"msg": "Admin added"}


# 3. GET member table
@app.get("/api/admin/see-member-table")
def see_members(member_id: int, db: Session = Depends(get_db)):
    verify_admin(member_id)
    logger.info(f"Admin {member_id} accessed the full member table.")
    
    logger.info("* DB SELECT: Fetching all Members")
    members = db.query(Member).all()

    return [
        {
            "MemberID": m.MemberID,
            "Name": m.FullName,
            "Email": m.Email,
            "Programme": m.Programme,
            "Branch": m.Branch,
            "BatchYear": m.BatchYear,
            "Contact": m.ContactNumber,
            "Age": m.Age,
            "Gender": m.Gender
        }
        for m in members
    ]


# 4. POST remove ride
@app.post("/api/admin/remove-ride")
def remove_ride(member_id: int, ride_id: str, db: Session = Depends(get_db)):
    verify_admin(member_id)

    logger.info(f"* DB SELECT: Fetching ActiveRide with RideID: {ride_id} for deletion")
    ride = db.query(ActiveRide).filter(ActiveRide.RideID == ride_id).first()
    if not ride:
        raise HTTPException(404, "Ride not found")

    db.delete(ride)
    db.commit()
    logger.info(f"* DB DELETE: Removed ActiveRide with RideID: {ride_id}")
    logger.info(f"Admin {member_id} forcibly removed RideID {ride_id}")
    return {"msg": "Ride removed"}


# 5. GET feedback table
@app.get("/api/admin/ridefeedback-table")
def get_feedback(member_id: int, db: Session = Depends(get_db)):
    verify_admin(member_id)

    logger.info("* DB SELECT: Fetching all RideFeedback")
    feedbacks = db.query(RideFeedback).all()

    return [
        {
            "RideID": f.RideID,
            "MemberID": f.MemberID,
            "Feedback": f.FeedbackText,
            "Category": f.FeedbackCategory,
            "SubmittedAt": f.SubmittedAt
        }
        for f in feedbacks
    ]


# 6. GET vehicles
@app.get("/api/admin/see-vehicle")
def get_vehicles(member_id: int, db: Session = Depends(get_db)):
    verify_admin(member_id)

    logger.info("* DB SELECT: Fetching all Vehicles")
    vehicles = db.query(Vehicle).all()

    return [
        {
            "VehicleID": v.VehicleID,
            "Type": v.VehicleType,
            "Capacity": v.MaxCapacity
        }
        for v in vehicles
    ]


# 7. POST add vehicle
@app.post("/api/admin/add-vehicle")
def add_vehicle(member_id: int, vehicle_type: str, max_capacity: int, db: Session = Depends(get_db)):
    verify_admin(member_id)

    v = Vehicle(VehicleType=vehicle_type, MaxCapacity=max_capacity)

    db.add(v)
    db.commit()
    db.refresh(v)
    logger.info(f"* DB INSERT: Added new Vehicle (Type: {vehicle_type}, Capacity: {max_capacity}, ID: {v.VehicleID})")
    logger.info(f"Admin {member_id} added a new vehicle type: {vehicle_type} (Capacity: {max_capacity})")
    return {"msg": "Vehicle added", "VehicleID": v.VehicleID}