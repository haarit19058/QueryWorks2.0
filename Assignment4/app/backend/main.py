import requests as http_requests # Add this to your imports at the top
from fastapi import FastAPI, Depends, HTTPException, Response, Request, status, Header 
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel
import jwt
import json
from datetime import datetime, timedelta, timezone

from models import * #Base, Member, ActiveRide, BookingRequest, MessageHistory, MemberStat
from typing import Any, Annotated

from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
import time
load_dotenv()

DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL") # Update to your MySQL connection string
GOOGLE_CLIENT_ID = os.environ.get("CLIENT_ID")
JWT_SECRET = os.environ.get("JWT_SECRET_KEY", "fallback-secret-key")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
ALGORITHM = "HS256"
ADMIN_FILE = "admin.json"

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
LOG_FILE_PATH = os.path.join(PARENT_DIR, "logs", "audit.log")

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
logger.setLevel(logging.ERROR) # Only log errors
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Override FastAPI and Uvicorn default loggers to use our file handler too
logging.getLogger("uvicorn.access").handlers = [console_handler, file_handler]
logging.getLogger("uvicorn.access").setLevel(logging.ERROR) # Suppress access logs
logging.getLogger("uvicorn.error").handlers = [console_handler, file_handler]
logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
logging.getLogger("fastapi").handlers = [console_handler, file_handler]
logging.getLogger("fastapi").setLevel(logging.ERROR)

# --- Database Setup ---
engine = create_engine(DATABASE_URL, pool_size=50, max_overflow=50, pool_timeout=30)
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

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    # Extract just the specific database error text
    error_msg = str(getattr(exc, "orig", exc))
    logger.error(f"Database error: {error_msg}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": error_msg}
    )

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
    platform: str | None = None
    reason: str | None = None
    price: int | None = None

# --- Auth Middleware ---
def get_current_user(request: Request, db: Session = Depends(get_db),
                      x_test_user_id: Annotated[str | None, Header(alias="X-Test-User-ID")] = None):
    # --- BYPASS AUTH FOR TESTING ---
    test_user_id = request.headers.get("X-Test-User-ID")
    if test_user_id:
        user = db.query(Member).filter(Member.MemberID == int(test_user_id)).first()
        if user:
            return user
    # -------------------------------
    
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
        logger.error(f"JWT DECODE ERROR: {e}")
        raise HTTPException(status_code=401, detail="Invalid session")

def create_cookie(response: Response, member_id: int):
    expire = datetime.now(IST) + timedelta(days=1)
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

@app.post("/auth/login") 
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
        
        # if not email.endswith('@iitgn.ac.in'):
        #     logger.warning(f"Failed login attempt: Unauthorized email domain ({email})")
        #     raise HTTPException(status_code=403, detail="Only IITGN emails allowed")

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
    return {"message": "Logged out"}

# --- Routes: Rides ---
@app.get("/rides")
def get_rides(db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    logger.info(f"Fetching all rides for UserID: {current_user.MemberID}")

    logger.info("* DB SELECT: Fetch ActiveRide + Member (JOIN)")
    rides = (
        db.query(ActiveRide, Member)
        .join(Member, ActiveRide.AdminID == Member.MemberID)
        .all()
    )
    logger.info(f"Fetched {len(rides)} rides")
    ride_ids = [r.ActiveRide.RideID for r in rides]

    passengers_data = (
        db.query(RidePassengerMap.RideID, Member.MemberID, Member.FullName, Member.ProfileImageURL)
        .join(Member, Member.MemberID == RidePassengerMap.PassengerID)
        .filter(RidePassengerMap.RideID.in_(ride_ids))
        .all()
    )

    # group passengers
    passenger_map = {}
    for p in passengers_data:
        passenger_map.setdefault(p.RideID, []).append({
            "MemberID": p.MemberID,
            "FullName": p.FullName,
            "ProfileImageURL": p.ProfileImageURL
        })

    result = []
    for ride, host in rides:
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
            "Status": ride.Status,
            "Passengers": passenger_map.get(ride.RideID, [])
        })

    return result

@app.post("/rides")
def create_ride(data: RideCreateData, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    # Identify max capacity from vehicle type
    # print(data.VehicleType)
    logger.info(f"Create ride request by UserID: {user.MemberID}")

    # Fetch vehicle
    logger.info(f"* DB SELECT: Fetch Vehicle for type: {data.VehicleType}")
    vehicle = db.query(Vehicle).filter(Vehicle.VehicleType==data.VehicleType).first()
    logger.info(f"Vehicle found → MaxCapacity: {vehicle.MaxCapacity}")
    # Add new ride
    new_ride = ActiveRide(
        AdminID       = user.MemberID,
        Source        = data.Source,
        Destination   = data.Destination,
        StartTime     = datetime.fromisoformat(data.StartTime),
        AvailableSeats = vehicle.MaxCapacity - 1,
        PassengerCount = 1,
        VehicleType   = data.VehicleType,
        FemaleOnly    = data.FemaleOnly,
        EstimatedTime = data.EstimatedTime
    )
    logger.info("* DB INSERT: Adding new ActiveRide")
    db.add(new_ride)
    db.flush()
    logger.info(f"New Ride created with RideID: {new_ride.RideID}")

    # Add creator as passenger
    logger.info("* DB INSERT: Adding creator to RidePassengerMap")
    db.add(RidePassengerMap(
        RideID      = new_ride.RideID,
        PassengerID = user.MemberID,
        IsConfirmed = True
    ))

    db.commit()
    logger.info(f"Ride successfully created → RideID: {new_ride.RideID}")
    return new_ride

@app.patch("/rides/{ride_id}/status")
def update_ride_status(
    ride_id: str,
    data: UpdateRideStatusData,
    db: Session = Depends(get_db),
    user: Member = Depends(get_current_user)
):
    logger.info(f"* DB SELECT: Fetching ActiveRide with RideID: {ride_id} for AdminID: {user.MemberID}")
    ride = db.query(ActiveRide).filter(
        ActiveRide.RideID == ride_id,
        ActiveRide.AdminID == user.MemberID
    ).first()
    if not ride:
        logger.warning(f"Failed status update attempt: Ride {ride_id} not found or unauthorized by UserID {user.MemberID}")
        raise HTTPException(404, "Ride not found or unauthorized")

    if data.status == "COMPLETED":
        # Archive to RideHistory
        if not data.platform or not data.price:
            raise HTTPException(400, "Both platform and price are required")
        db.add(RideHistory(
            RideID      = ride.RideID,
            AdminID     = ride.AdminID,
            RideDate    = ride.StartTime.date(),
            StartTime   = ride.StartTime.time(),
            Source      = ride.Source,
            Destination = ride.Destination,
            Platform    = data.platform,
            Price       = data.price,
            FemaleOnly  = ride.FemaleOnly,
        ))

        passengers = db.query(RidePassengerMap).filter(
            RidePassengerMap.RideID == ride_id,
            RidePassengerMap.IsConfirmed == True
        ).all()
        passenger_ids = [p.PassengerID for p in passengers]

        stats = {
            s.MemberID: s
            for s in db.query(MemberStat)
            .filter(MemberStat.MemberID.in_(passenger_ids))
            .all()
        }

        for p in passengers:
            stat = stats.get(p.PassengerID)

            if not stat:
                stat = MemberStat(
                    MemberID=p.PassengerID,
                    AverageRating=0.0,
                    TotalRidesTaken=0,
                    TotalRidesHosted=0,
                    NumberOfRatings=0
                )
                db.add(stat)
                stats[p.PassengerID] = stat

            if p.PassengerID == ride.AdminID:
                stat.TotalRidesHosted += 1
            else:
                stat.TotalRidesTaken += 1

        db.delete(ride)
        db.commit()
        return {"message": "Ride completed and archived"}

    if data.status == "CANCELLED":
        if not data.reason:
            raise HTTPException(400, "Cancellation reason required")
        db.add(Cancellation(
            RideID             = ride.RideID,
            MemberID           = user.MemberID,
            CancellationReason = data.reason,
        ))
        db.delete(ride)
        db.commit()
        return {"message": "Ride cancelled"}

    ride.Status = data.status
    db.commit()
    return {"message": "Status updated"}

class FeedbackPayload(BaseModel):
    RideID: str
    FeedbackText: str
    FeedbackCategory: str  # "Safety" | "Comfort" | "Punctuality"

@app.post("/feedback")
def submit_feedback(
    data: FeedbackPayload,
    db: Session = Depends(get_db),
    user: Member = Depends(get_current_user)
):
    # Ride is already in history now
    logger.info(f"* DB SELECT: Checking RideHistory for RideID {data.RideID}")
    ride = db.query(RideHistory).filter(RideHistory.RideID == data.RideID).first()
    if not ride:
        logger.warning(f"Ride not found in history: {data.RideID}")
        raise HTTPException(404, "Ride not found in history")

    # Verify user was a passenger or the host
    logger.info(f"* DB SELECT: Verifying if user {user.MemberID} was involved in Ride {data.RideID}")
    was_involved = (
        ride.AdminID == user.MemberID or
        db.query(RidePassengerMap).filter(
            RidePassengerMap.RideID == data.RideID,
            RidePassengerMap.PassengerID == user.MemberID,
            RidePassengerMap.IsConfirmed == True
        ).first() is not None
    )
    if not was_involved:
        raise HTTPException(403, "You were not part of this ride")
    logger.info(f"* DB SELECT: Checking if feedback already submitted by user {user.MemberID}")
    already_submitted = db.query(RideFeedback).filter(
        RideFeedback.RideID == data.RideID,
        RideFeedback.MemberID == user.MemberID
    ).first()
    if already_submitted:
        raise HTTPException(400, "Feedback already submitted")

    db.add(RideFeedback(
        RideID           = data.RideID,
        MemberID         = user.MemberID,
        FeedbackText     = data.FeedbackText,
        FeedbackCategory = data.FeedbackCategory,
    ))
    db.commit()
    logger.info(f"* DB INSERT: Feedback added for RideID {data.RideID} by MemberID {user.MemberID}")
    return {"message": "Feedback submitted"}

# Separate rating endpoint — called once per person being rated
class RatingPayload(BaseModel):
    RideID: str
    ReceiverMemberID: int
    Rating: float
    RatingComment: str | None = None

@app.post("/ratings")
def submit_rating(data: RatingPayload, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    # Prevent duplicate
    logger.info(f"* DB SELECT: Checking existing rating by user {user.MemberID} for RideID {data.RideID}")
    existing = db.query(MemberRating).filter(
        MemberRating.RideID == data.RideID,
        MemberRating.SenderMemberID == user.MemberID,
        MemberRating.ReceiverMemberID == data.ReceiverMemberID,
    ).first()
    if existing:
        raise HTTPException(400, "Already rated this member for this ride")

    db.add(MemberRating(
        RideID           = data.RideID,
        SenderMemberID   = user.MemberID,
        ReceiverMemberID = data.ReceiverMemberID,
        Rating           = data.Rating,
        RatingComment    = data.RatingComment,
    ))
    logger.info(f"* DB SELECT: Fetching MemberStat for ReceiverMemberID {data.ReceiverMemberID}")
    stat = db.query(MemberStat)\
         .filter(MemberStat.MemberID == data.ReceiverMemberID)\
         .with_for_update()\
         .first()
    if stat:
        total = stat.AverageRating * stat.NumberOfRatings
        stat.NumberOfRatings += 1
        stat.AverageRating = (total + data.Rating) / stat.NumberOfRatings

    db.commit()
    logger.info(f"* DB UPDATE: Rating submitted for MemberID {data.ReceiverMemberID} by MemberID {user.MemberID}")
    return {"message": "Rating submitted"}

@app.get("/ride-history")
def get_ride_history(db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    logger.info(f"* DB SELECT: Fetching rides hosted by MemberID {user.MemberID}")
    hosted = db.query(RideHistory).filter(RideHistory.AdminID == user.MemberID).all()

    logger.info(f"* DB SELECT: Fetching rides taken by MemberID {user.MemberID}")
    taken = (
        db.query(RideHistory)
        .join(RidePassengerMap, RideHistory.RideID == RidePassengerMap.RideID)
        .filter(
            RidePassengerMap.PassengerID == user.MemberID,
            RideHistory.AdminID != user.MemberID  # ← exclude rides they hosted
        )
        .all()
    )

    def serialize(ride: RideHistory, role: str):
        has_feedback = db.query(RideFeedback).filter(
            RideFeedback.RideID == ride.RideID,
            RideFeedback.MemberID == user.MemberID
        ).first() is not None
        
        admin = db.query(Member).filter(Member.MemberID == ride.AdminID).first()

        passengers = (
            db.query(Member.MemberID, Member.FullName)
            .join(RidePassengerMap, Member.MemberID == RidePassengerMap.PassengerID)
            .filter(RidePassengerMap.RideID == ride.RideID)
            .all()
        )
        
        return {
            **{c.name: getattr(ride, c.name) for c in ride.__table__.columns},
            "Role":       role,
            "Passengers": [{"MemberID": p.MemberID, "FullName": p.FullName} for p in passengers],
            "AdminName":   admin.FullName if admin else "Unknown",
            "HasFeedback": has_feedback,
        }

    return (
        [serialize(r, "HOST")      for r in hosted] +
        [serialize(r, "PASSENGER") for r in taken]
    )

# --- Routes: Bookings ---
# This api is for the AvailableRides page to show the user correct UI
@app.get("/booking-requests")
def get_bookings(db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    # The frontend fetches requests for the current user
    logger.info(f"* DB SELECT: Fetching booking requests for MemberID {user.MemberID}")
    requests = db.query(BookingRequest).filter(BookingRequest.PassengerID == user.MemberID).all()
    return requests

# My booking requests (send by by)
@app.post("/booking-requests")
def request_join(data: RequestJoinData, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    logger.info(f"* DB SELECT: Fetching pending booking requests for rides hosted by MemberID {user.MemberID}")
    new_req = BookingRequest(RideID=data.RideID, PassengerID=user.MemberID)
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    logger.info(f"* DB INSERT: Booking request created for RideID {data.RideID} by MemberID {user.MemberID}")
    return new_req

# Booking requests sent to admin (sent to me)
@app.get("/booking-requests/pending")
def get_pending_requests(
    db: Session = Depends(get_db),
    user: Member = Depends(get_current_user)
):
    results = (
        db.query(BookingRequest)
        .join(ActiveRide, BookingRequest.RideID == ActiveRide.RideID)
        .join(Member, BookingRequest.PassengerID == Member.MemberID)
        .filter(
            ActiveRide.AdminID == user.MemberID,
            BookingRequest.RequestStatus == "PENDING"
        )
        .add_columns(Member.FullName.label("PassengerName"))
        .all()
    )

    return [
        {
            **row.BookingRequest.__dict__,
            "PassengerName": row.PassengerName
        }
        for row in results
    ]

@app.patch("/booking-requests/{request_id}")
def update_booking(request_id: int, data: UpdateRequestData, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    logger.info(f"* DB SELECT: Fetching booking request {request_id}")
    req = db.query(BookingRequest).filter(BookingRequest.RequestID == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if req.RequestStatus == data.RequestStatus:
        return {"message": "Request already in the desired state"}
    
    req.RequestStatus = data.RequestStatus
    
    if data.RequestStatus == "APPROVED":
        ride = db.query(ActiveRide).filter(ActiveRide.RideID == req.RideID).with_for_update().first()
        if ride and ride.AvailableSeats > 0: 
            ride.AvailableSeats -= 1
            ride.PassengerCount += 1
            db.add(RidePassengerMap(
                RideID      = req.RideID,
                PassengerID = req.PassengerID,
                IsConfirmed = True
            ))
            
            db.commit()
            print(f"* DB UPDATE: Booking request {request_id} status updated to {data.RequestStatus}")
            return {"message": "Request updated"}
        
    db.commit()
    return {"message": "Not Enough Seats!"}
 
# --- Routes: Messages ---
@app.get("/messages")
def get_messages(rideId: str, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    messages = (
        db.query(MessageHistory, Member)
        .join(Member, MessageHistory.SenderID == Member.MemberID)
        .filter(MessageHistory.RideID == rideId)
        .order_by(MessageHistory.Timestamp.asc())
        .all()
    )

    return [
        {
            "MessageID": msg.MessageID,
            "RideID": msg.RideID,
            "SenderID": msg.SenderID,
            "SenderName": member.FullName if member else "Unknown",
            "SenderAvatar": member.ProfileImageURL if member else "",
            "MessageText": msg.MessageText,
            "Timestamp": msg.Timestamp.isoformat(),
            "IsRead": msg.IsRead
        }
        for msg, member in messages
    ]

@app.post("/messages")
def send_message(data: MessageCreateData, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    new_msg = MessageHistory(RideID=data.RideID, SenderID=user.MemberID, MessageText=data.MessageText)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)

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

@app.get("/members/{member_id}")
def get_user_profile(member_id: int, db: Session = Depends(get_db)) -> Any:
    """
    Fetch a user's profile details along with their ride statistics.
    """
    # Query both Member and MemberStat tables using an outer join
    result = (
        db.query(Member, MemberStat)
        .outerjoin(MemberStat, Member.MemberID == MemberStat.MemberID)
        .filter(Member.MemberID == member_id)
        .first()
    )

    # If no member is found, return a 404
    if not result:
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
    with open(ADMIN_FILE, "r") as f:
        return json.load(f)

def write_admin_file(data):
    with open(ADMIN_FILE, "w") as f:
        json.dump(data, f, indent=4)

def is_admin(member_id: int) -> bool:
    data = read_admin_file()
    return member_id in data.get("Admin_Member_Ids", [])

def verify_admin(member_id: int):
    if not is_admin(member_id):
        raise HTTPException(status_code=403, detail="Not an admin")


# ------------------ PUBLIC CHECK ------------------
@app.get("/is-admin")
def check_admin(member_id: int):
    return {"is_admin": is_admin(member_id)}


# ------------------ ADMIN APIs ------------------

# 1. GET current admins
@app.get("/admin/current-admins")
def get_current_admins(member_id: int, db: Session = Depends(get_db)):
    verify_admin(member_id)

    data = read_admin_file()
    ids = data.get("Admin_Member_Ids", [])

    admins = db.query(Member).filter(Member.MemberID.in_(ids)).all()

    return [
        {"MemberID": a.MemberID, "FullName": a.FullName, "Email": a.Email}
        for a in admins
    ]


# 2. POST add admin
@app.post("/admin/add-admin")
def add_admin(member_id: int, email: str, db: Session = Depends(get_db)):
    verify_admin(member_id)

    member = db.query(Member).filter(Member.Email == email).first()
    if not member:
        raise HTTPException(404, "Member not found")

    data = read_admin_file()

    if member.MemberID in data["Admin_Member_Ids"]:
        return {"msg": "Already admin"}

    data["Admin_Member_Ids"].append(member.MemberID)
    data["Admin_Emails"].append(email)

    write_admin_file(data)

    return {"msg": "Admin added"}


# 3. GET member table
@app.get("/admin/see-member-table")
def see_members(member_id: int, db: Session = Depends(get_db)):
    verify_admin(member_id)

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
@app.post("/admin/remove-ride")
def remove_ride(member_id: int, ride_id: str, db: Session = Depends(get_db)):
    verify_admin(member_id)

    ride = db.query(ActiveRide).filter(ActiveRide.RideID == ride_id).first()
    if not ride:
        raise HTTPException(404, "Ride not found")

    db.delete(ride)
    db.commit()

    return {"msg": "Ride removed"}


# 5. GET feedback table
@app.get("/admin/ridefeedback-table")
def get_feedback(member_id: int, db: Session = Depends(get_db)):
    verify_admin(member_id)

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
@app.get("/admin/see-vehicle")
def get_vehicles(member_id: int, db: Session = Depends(get_db)):
    verify_admin(member_id)

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
@app.post("/admin/add-vehicle")
def add_vehicle(member_id: int, vehicle_type: str, max_capacity: int, db: Session = Depends(get_db)):
    verify_admin(member_id)

    v = Vehicle(VehicleType=vehicle_type, MaxCapacity=max_capacity)

    db.add(v)
    db.commit()
    db.refresh(v)

    return {"msg": "Vehicle added", "VehicleID": v.VehicleID}