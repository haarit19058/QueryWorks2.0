import requests as http_requests # Add this to your imports at the top
from fastapi import FastAPI, Depends, HTTPException, Response, Request, status, Header 
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, func, text, event
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
import hashlib
load_dotenv()

SHARD0_URL = os.environ.get("SHARD0_DATABASE_URL")
SHARD1_URL = os.environ.get("SHARD1_DATABASE_URL")
SHARD2_URL = os.environ.get("SHARD2_DATABASE_URL")

GOOGLE_CLIENT_ID = os.environ.get("CLIENT_ID")
JWT_SECRET = os.environ.get("JWT_SECRET_KEY", "fallback-secret-key")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
ALGORITHM = "HS256"
ADMIN_FILE = "admin.json"
RIDE_DIRECTORY_FILE = "ride_shard_directory.json"

def get_ride_shard_map() -> dict:
    if not os.path.exists(RIDE_DIRECTORY_FILE):
        return {}
    with open(RIDE_DIRECTORY_FILE, "r") as f:
        return json.load(f)

def update_ride_directory(ride_id: str, shard_id: int):
    mapping = get_ride_shard_map()
    mapping[ride_id] = shard_id
    with open(RIDE_DIRECTORY_FILE, "w") as f:
        json.dump(mapping, f, indent=4)

def get_shard_for_ride(ride_id: str) -> int:
    mapping = get_ride_shard_map()
    return mapping.get(ride_id, 0) # Fallback to 0 if not found

GLOBAL_NEXT_MEMBER_ID = None

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
logger.setLevel(logging.INFO) # Changed to INFO so you can see all the shard routing mechanisms
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
engine0 = create_engine(SHARD0_URL, pool_size=50, max_overflow=50, pool_timeout=30)
engine1 = create_engine(SHARD1_URL, pool_size=50, max_overflow=50, pool_timeout=30)
engine2 = create_engine(SHARD2_URL, pool_size=50, max_overflow=50, pool_timeout=30)

for engine in (engine0, engine1, engine2):
    @event.listens_for(engine, "connect")
    def configure_fk_checks(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("SET foreign_key_checks = 0;")
        cursor.close()

SessionLocal0 = sessionmaker(autocommit=False, autoflush=False, bind=engine0)
SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)

def get_db_shards():
    db0, db1, db2 = SessionLocal0(), SessionLocal1(), SessionLocal2()
    try:
        yield {0: db0, 1: db1, 2: db2}
    finally:
        db0.close()
        db1.close()
        db2.close()

# Keeping a fallback get_db to prevent unmigrated routes from completely breaking
def get_db():
    db = SessionLocal0()
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
    # We can inspect the exception or request to potentially identify the shard, 
    # but the simplest way is to include shard info in the logging where the error occurs if possible.
    logger.error(f"Database error: {error_msg} (Request: {request.url.path})")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": error_msg}
    )

def get_shard_id(member_id: int) -> int:
    """Computes the shard ID using SHA-256 hash of the MemberID modulo 3"""
    hash_digest = hashlib.sha256(str(member_id).encode()).hexdigest()
    return int(hash_digest, 16) % 3

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
def get_current_user(request: Request, shards: dict = Depends(get_db_shards),
                      x_test_user_id: Annotated[str | None, Header(alias="X-Test-User-ID")] = None):
    # --- BYPASS AUTH FOR TESTING ---
    test_user_id = request.headers.get("X-Test-User-ID")
    if test_user_id:
        shard_id = get_shard_id(int(test_user_id))
        db = shards[shard_id]
        user = db.query(Member).filter(Member.MemberID == int(test_user_id)).first()
        if user:
            request.state.db = db
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
        
        shard_id = get_shard_id(member_id)
        db = shards[shard_id]

        logger.info(f"Using Shard {shard_id} for fetching Member data during get_current_user middleware")
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
def login(data: GoogleLoginData, response: Response, shards: dict = Depends(get_db_shards)):
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
        
        logger.info(f"Using Scatter Gather to check all shards for Email during login")
        
        user = None
        for shard_num, db in shards.items():
            logger.info(f"* DB SELECT: Checking Member table on Shard {shard_num} for Email: {email}")
            try:
                user = db.query(Member).filter(Member.Email == email).first()
                if user:
                    break
            except SQLAlchemyError as e:
                logger.error(f"Shard {shard_num} failed during login email check: {str(e)}")
                continue
        
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
def signup(data: SignupData, response: Response, shards: dict = Depends(get_db_shards)):
    global GLOBAL_NEXT_MEMBER_ID
    
    # 1. Initialize the global counter on first signup (or after restart) if needed
    if GLOBAL_NEXT_MEMBER_ID is None:
        max_id = 0
        for shard_id, db in shards.items():
            curr_max = db.query(func.max(Member.MemberID)).scalar()
            if curr_max and curr_max > max_id:
                max_id = curr_max
        GLOBAL_NEXT_MEMBER_ID = max_id + 1
            
    next_id = GLOBAL_NEXT_MEMBER_ID
    GLOBAL_NEXT_MEMBER_ID += 1
    
    shard_target = get_shard_id(next_id)
    target_db = shards[shard_target]

    logger.info(f"Using Shard {shard_target} to register new user {data.Email}")
    new_user = Member(
        MemberID=next_id, # Explicitly assign to enforce global sequence across shards
        GoogleSub=data.google_sub, FullName=data.FullName, Email=data.Email,
        ProfileImageURL=data.ProfileImageURL, Programme=data.Programme,
        Branch=data.Branch, BatchYear=data.BatchYear, ContactNumber=data.ContactNumber,
        Gender=data.Gender, Age=data.Age
    )
    target_db.add(new_user)
    target_db.commit()
    target_db.refresh(new_user)
    
    logger.info(f"* DB INSERT: Member physically stored permanently over Shard {shard_target} (Email: {data.Email}, ID: {new_user.MemberID})")
    create_cookie(response, new_user.MemberID)
    logger.info(f"New user signed up successfully: {new_user.Email} (ID: {new_user.MemberID})")
    return {"user": new_user}

@app.get("/auth/me")
def get_me(user: Member = Depends(get_current_user)):
    logger.info(f"API /auth/me requested -> Data retrieved from Shard {get_shard_id(user.MemberID)}")
    return user

@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie("session_token")
    return {"message": "Logged out"}

# --- Routes: Rides ---
@app.get("/rides")
def get_rides(shards: dict = Depends(get_db_shards), current_user: Member = Depends(get_current_user)):
    logger.info(f"Fetching all rides across shards for UserID: {current_user.MemberID}")

    result = []
    
    # SCATTER: Query all 3 shards
    for shard_num, db in shards.items():
        try:
            logger.info(f"* DB SELECT: Fetch ActiveRide + Member (JOIN) from Shard {shard_num}")
            rides = (
                db.query(ActiveRide, Member)
                .join(Member, ActiveRide.AdminID == Member.MemberID)
                .all()
            )
            logger.info(f"Fetched {len(rides)} rides from Shard {shard_num}")
            
            ride_ids = [r.ActiveRide.RideID for r in rides]
            if not ride_ids:
                continue

            # Fetch passengers WITHOUT joining Member table, as passengers are on different shards
            passengers_raw = (
                db.query(RidePassengerMap.RideID, RidePassengerMap.PassengerID)
                .filter(RidePassengerMap.RideID.in_(ride_ids), RidePassengerMap.IsConfirmed == True)
                .all()
            )

            # group passengers and resolve names globally
            passenger_map = {}
            for p in passengers_raw:
                p_shard = shards[get_shard_id(p.PassengerID)]
                try:
                    p_member = p_shard.query(Member).filter(Member.MemberID == p.PassengerID).first()
                    p_name = p_member.FullName if p_member else "Unknown"
                    p_img = p_member.ProfileImageURL if p_member else ""
                except Exception:
                    p_name = "Unknown"
                    p_img = ""
                    
                passenger_map.setdefault(p.RideID, []).append({
                    "MemberID": p.PassengerID,
                    "FullName": p_name,
                    "ProfileImageURL": p_img
                })

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
        except SQLAlchemyError as e:
            # FAULT TOLERANCE: Ignore current shard
            logger.error(f"Shard {shard_num} failed during GET /rides: {str(e)}")
            continue

    return result

@app.post("/rides")
def create_ride(data: RideCreateData, shards: dict = Depends(get_db_shards), user: Member = Depends(get_current_user)):
    # 1. Select user's shard
    shard_id = get_shard_id(user.MemberID)
    db = shards[shard_id]
    
    logger.info(f"Using Shard {shard_id} to create a new ride for AdminID {user.MemberID}")
    
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
    logger.info(f"Ride successfully created and physically stored on Shard {shard_id} → RideID: {new_ride.RideID}")
    
    update_ride_directory(new_ride.RideID, shard_id)
    return new_ride

@app.patch("/rides/{ride_id}/status")
def update_ride_status(
    ride_id: str,
    data: UpdateRideStatusData,
    shards: dict = Depends(get_db_shards),
    user: Member = Depends(get_current_user)
):
    shard_id = get_shard_for_ride(ride_id)
    db = shards[shard_id]

    logger.info(f"Using Shard {shard_id} for updating status of ride {ride_id}")
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
        
        # When compiling final passenger stats, passengers might exist in different shards originally, 
        # but the MemberStat map is generated in the Host's shard here for local ride processing.
        # Alternatively, we should update each passenger's MemberStat globally.
        for p in passengers:
            passenger_shard = shards[get_shard_id(p.PassengerID)]
            try:
                stat = passenger_shard.query(MemberStat).filter(MemberStat.MemberID == p.PassengerID).first()

                if not stat:
                    stat = MemberStat(
                        MemberID=p.PassengerID,
                        AverageRating=0.0,
                        TotalRidesTaken=0,
                        TotalRidesHosted=0,
                        NumberOfRatings=0
                    )
                    passenger_shard.add(stat)

                if p.PassengerID == ride.AdminID:
                    stat.TotalRidesHosted += 1
                else:
                    stat.TotalRidesTaken += 1
                    
                passenger_shard.commit()
            except SQLAlchemyError:
                passenger_shard.rollback()

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
    shards: dict = Depends(get_db_shards),
    user: Member = Depends(get_current_user)
):
    shard_id = get_shard_for_ride(data.RideID)
    db = shards[shard_id]
    
    logger.info(f"Using Shard {shard_id} for submitting feedback on ride {data.RideID}")

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
    logger.info(f"* DB INSERT: Feedback securely logged and mathematically stored on Shard {shard_id} for RideID {data.RideID} by MemberID {user.MemberID}")
    return {"message": "Feedback submitted"}

# Separate rating endpoint — called once per person being rated
class RatingPayload(BaseModel):
    RideID: str
    ReceiverMemberID: int
    Rating: float
    RatingComment: str | None = None

@app.post("/ratings")
def submit_rating(data: RatingPayload, shards: dict = Depends(get_db_shards), user: Member = Depends(get_current_user)):
    shard_id = get_shard_for_ride(data.RideID)
    db = shards[shard_id]

    logger.info(f"Using Shard {shard_id} for inserting rating for ride {data.RideID}")

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
    db.commit() # Save the rating on the Ride's Shard
    
    # Update Member stats on the Receiver's shard
    receiver_shard = shards[get_shard_id(data.ReceiverMemberID)]
    logger.info(f"* DB SELECT: Fetching MemberStat for ReceiverMemberID {data.ReceiverMemberID} from Shard {get_shard_id(data.ReceiverMemberID)}")
    try:
        stat = receiver_shard.query(MemberStat)\
             .filter(MemberStat.MemberID == data.ReceiverMemberID)\
             .with_for_update()\
             .first()
        if stat:
            total = stat.AverageRating * stat.NumberOfRatings
            stat.NumberOfRatings += 1
            stat.AverageRating = (total + data.Rating) / stat.NumberOfRatings
            receiver_shard.commit()
        else:
            # Create if doesn't exist
            new_stat = MemberStat(
                MemberID=data.ReceiverMemberID,
                AverageRating=data.Rating,
                NumberOfRatings=1,
                TotalRidesHosted=0,
                TotalRidesTaken=0
            )
            receiver_shard.add(new_stat)
            receiver_shard.commit()
    except SQLAlchemyError as e:
        receiver_shard.rollback()
        logger.error(f"Failed to update member stats: {e}")

    logger.info(f"* DB UPDATE: Rating submitted for MemberID {data.ReceiverMemberID} by MemberID {user.MemberID}")
    return {"message": "Rating submitted"}

@app.get("/ride-history")
def get_ride_history(shards: dict = Depends(get_db_shards), user: Member = Depends(get_current_user)):
    # SCATTER-GATHER: fetch ride history for user (host or passenger) from all shards
    all_hosted = []
    all_taken = []
    
    def serialize(ride: RideHistory, role: str, db: Session):
        has_feedback = db.query(RideFeedback).filter(
            RideFeedback.RideID == ride.RideID,
            RideFeedback.MemberID == user.MemberID
        ).first() is not None
        
        # We need the AdminName. Since member data is on Admin's shard, it might or might not be here.
        # But if the Ride is here, the Admin data MUST be here!
        admin = db.query(Member).filter(Member.MemberID == ride.AdminID).first()

        passengers_raw = db.query(RidePassengerMap.PassengerID).filter(RidePassengerMap.RideID == ride.RideID).all()
        
        passenger_list = []
        for (p_id,) in passengers_raw:
            p_shard = shards[get_shard_id(p_id)]
            try:
                p_member = p_shard.query(Member).filter(Member.MemberID == p_id).first()
                if p_member:
                    passenger_list.append({"MemberID": p_id, "FullName": p_member.FullName})
                else:
                    passenger_list.append({"MemberID": p_id, "FullName": "Unknown"})
            except Exception:
                passenger_list.append({"MemberID": p_id, "FullName": "Unknown"})
        
        return {
            **{c.name: getattr(ride, c.name) for c in ride.__table__.columns},
            "Role":       role,
            "Passengers": passenger_list,
            "AdminName":   admin.FullName if admin else "Unknown",
            "HasFeedback": has_feedback,
        }

    logger.info(f"Fetching ride history across shards for MemberID {user.MemberID}")
    for shard_num, db in shards.items():
        try:
            logger.info(f"Checking Shard {shard_num} for ride history of user {user.MemberID}")
            # Hosted
            hosted = db.query(RideHistory).filter(RideHistory.AdminID == user.MemberID).all()
            for r in hosted:
                all_hosted.append(serialize(r, "HOST", db))
                
            # Taken (Passenger)
            taken_query = (
                db.query(RideHistory)
                .join(RidePassengerMap, RideHistory.RideID == RidePassengerMap.RideID)
                .filter(
                    RidePassengerMap.PassengerID == user.MemberID,
                    RideHistory.AdminID != user.MemberID
                ).all()
            )
            for r in taken_query:
                all_taken.append(serialize(r, "PASSENGER", db))
                
        except SQLAlchemyError as e:
            logger.error(f"Shard {shard_num} failed during GET /ride-history: {str(e)}")
            continue

    return all_hosted + all_taken

# --- Routes: Bookings ---
# This api is for the AvailableRides page to show the user correct UI
@app.get("/booking-requests")
def get_bookings(shards: dict = Depends(get_db_shards), user: Member = Depends(get_current_user)):
    requests = []
    logger.info(f"Gathering booking requests from all shards for user {user.MemberID}")
    # Scatter gather since a user's booking request exists on the Ride's host shard
    for shard_num, db in shards.items():
        try:
            logger.info(f"Querying Shard {shard_num} for booking requests")
            shard_reqs = db.query(BookingRequest).filter(BookingRequest.PassengerID == user.MemberID).all()
            requests.extend(shard_reqs)
        except SQLAlchemyError:
            continue
    return requests

# My booking requests (send by by)
@app.post("/booking-requests")
def request_join(data: RequestJoinData, shards: dict = Depends(get_db_shards), user: Member = Depends(get_current_user)):
    shard_id = get_shard_for_ride(data.RideID)
    db = shards[shard_id]
    
    logger.info(f"Using Shard {shard_id} for creating a booking request on ride {data.RideID}")
    logger.info(f"* DB SELECT: Fetching pending booking requests for rides hosted by MemberID {user.MemberID}")
    new_req = BookingRequest(RideID=data.RideID, PassengerID=user.MemberID)
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    logger.info(f"* DB INSERT: Booking request securely stored on Shard {shard_id} for RideID {data.RideID} by MemberID {user.MemberID}")
    return new_req

# Booking requests sent to admin (sent to me)
@app.get("/booking-requests/pending")
def get_pending_requests(
    shards: dict = Depends(get_db_shards),
    user: Member = Depends(get_current_user)
):
    shard_id = get_shard_id(user.MemberID)
    db = shards[shard_id]
    
    logger.info(f"Using Shard {shard_id} to query pending booking requests sent to admin {user.MemberID}")
    
    # Query bookings and rides on the host's shard
    results = (
        db.query(BookingRequest)
        .join(ActiveRide, BookingRequest.RideID == ActiveRide.RideID)
        .filter(
            ActiveRide.AdminID == user.MemberID,
            BookingRequest.RequestStatus == "PENDING"
        )
        .all()
    )

    final_results = []
    for req in results:
        # The passenger may live on a completely different shard, query them dynamically
        passenger_shard = get_shard_id(req.PassengerID)
        try:
            passenger_db = shards[passenger_shard]
            passenger = passenger_db.query(Member).filter(Member.MemberID == req.PassengerID).first()
            passenger_name = passenger.FullName if passenger else "Unknown"
        except Exception:
            passenger_name = "Unknown"
            
        req_dict = {k: v for k, v in req.__dict__.items() if not k.startswith("_")}
        req_dict["PassengerName"] = passenger_name
        final_results.append(req_dict)

    return final_results

@app.patch("/booking-requests/{request_id}")
def update_booking(request_id: int, data: UpdateRequestData, shards: dict = Depends(get_db_shards), user: Member = Depends(get_current_user)):
    shard_id = get_shard_id(user.MemberID)
    db = shards[shard_id]
    
    logger.info(f"Using Shard {shard_id} to update booking request {request_id}")
    logger.info(f"* DB SELECT: Fetching booking request {request_id}")
    req = db.query(BookingRequest).filter(BookingRequest.RequestID == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if req.RequestStatus == data.RequestStatus:
        return {"message": "Request already in the desired state"}
    
    if data.RequestStatus == "APPROVED":
        ride = db.query(ActiveRide).filter(ActiveRide.RideID == req.RideID).with_for_update().first()
        if not ride:
            raise HTTPException(status_code=404, detail="Ride not found")
            
        if ride.AvailableSeats <= 0:
            raise HTTPException(status_code=400, detail="Not Enough Seats!")
            
        ride.AvailableSeats -= 1
        ride.PassengerCount += 1
        db.add(RidePassengerMap(
            RideID      = req.RideID,
            PassengerID = req.PassengerID,
            IsConfirmed = True
        ))
    
    # Commit the changes for both approved and rejected
    req.RequestStatus = data.RequestStatus
    db.commit()
    logger.info(f"* DB UPDATE: Booking request {request_id} status updated to {data.RequestStatus}")
    return {"message": f"Request {data.RequestStatus.lower()}"}
 
# --- Routes: Messages ---
@app.get("/messages")
def get_messages(rideId: str, shards: dict = Depends(get_db_shards), user: Member = Depends(get_current_user)):
    shard_id = get_shard_for_ride(rideId)
    db = shards[shard_id]
    
    logger.info(f"Using Shard {shard_id} to query messages for ride {rideId}")
    
    # We may need to gather user profiles from other shards if the sender is not on the same shard.
    messages_query = (
        db.query(MessageHistory)
        .filter(MessageHistory.RideID == rideId)
        .order_by(MessageHistory.Timestamp.asc())
        .all()
    )

    # Resolve sender details via scatter-gather since senders might be from different shards
    sender_ids = {msg.SenderID for msg in messages_query}
    senders = {}
    for sender_id in sender_ids:
        sender_shard = shards[get_shard_id(sender_id)]
        member = sender_shard.query(Member).filter(Member.MemberID == sender_id).first()
        if member:
            senders[sender_id] = member

    return [
        {
            "MessageID": msg.MessageID,
            "RideID": msg.RideID,
            "SenderID": msg.SenderID,
            "SenderName": senders.get(msg.SenderID).FullName if senders.get(msg.SenderID) else "Unknown",
            "SenderAvatar": senders.get(msg.SenderID).ProfileImageURL if senders.get(msg.SenderID) else "",
            "MessageText": msg.MessageText,
            "Timestamp": msg.Timestamp.isoformat(),
            "IsRead": msg.IsRead
        }
        for msg in messages_query
    ]

@app.post("/messages")
def send_message(data: MessageCreateData, shards: dict = Depends(get_db_shards), user: Member = Depends(get_current_user)):
    shard_id = get_shard_for_ride(data.RideID)
    db = shards[shard_id]
    
    logger.info(f"Using Shard {shard_id} to record a new message for ride {data.RideID}")
    
    new_msg = MessageHistory(RideID=data.RideID, SenderID=user.MemberID, MessageText=data.MessageText)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)

    logger.info(f"Message successfully stored on Shard {shard_id} Database for Ride {data.RideID}")

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
def get_user_profile(member_id: int, shards: dict = Depends(get_db_shards)) -> Any:
    """
    Fetch a user's profile details along with their ride statistics.
    """
    shard_id = get_shard_id(member_id)
    db = shards[shard_id]
    
    logger.info(f"Using Shard {shard_id} to fetch member profile {member_id}")
    
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
def get_current_admins(member_id: int, shards: dict = Depends(get_db_shards)):
    verify_admin(member_id)

    data = read_admin_file()
    ids = data.get("Admin_Member_Ids", [])

    admins = []
    logger.info("Using Scatter Gather (All Shards) to fetch active admins")
    for shard_num, db in shards.items():
        try:
            admins.extend(db.query(Member).filter(Member.MemberID.in_(ids)).all())
        except SQLAlchemyError:
            continue

    return [
        {"MemberID": a.MemberID, "FullName": a.FullName, "Email": a.Email}
        for a in admins
    ]


# 2. POST add admin
@app.post("/admin/add-admin")
def add_admin(member_id: int, email: str, shards: dict = Depends(get_db_shards)):
    verify_admin(member_id)

    member = None
    logger.info(f"Using Scatter Gather to dynamically locate user block tied to email {email}")
    for shard_num, db in shards.items():
        try:
            member = db.query(Member).filter(Member.Email == email).first()
            if member: break
        except SQLAlchemyError:
            continue
            
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
def see_members(member_id: int, shards: dict = Depends(get_db_shards)):
    verify_admin(member_id)

    members = []
    logger.info("Using Scatter Gather (All Shards) to fetch complete member directory for admin panel")
    for shard_num, db in shards.items():
        try:
            members.extend(db.query(Member).all())
        except SQLAlchemyError:
            continue

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
def remove_ride(member_id: int, ride_id: str, shards: dict = Depends(get_db_shards)):
    verify_admin(member_id)
    
    shard_id = get_shard_for_ride(ride_id)
    db = shards[shard_id]

    logger.info(f"Using Shard {shard_id} to forcefully remove ride {ride_id} by Super Admin {member_id}")
    ride = db.query(ActiveRide).filter(ActiveRide.RideID == ride_id).first()
    if not ride:
        raise HTTPException(404, "Ride not found")

    db.delete(ride)
    db.commit()

    return {"msg": "Ride removed"}


# 5. GET feedback table
@app.get("/admin/ridefeedback-table")
def get_feedback(member_id: int, shards: dict = Depends(get_db_shards)):
    verify_admin(member_id)

    logger.info("Admin Action: Utilizing Scatter Gather Strategy to Fetch All Feedback")

    feedbacks = []
    for shard_num, db in shards.items():
        try:
            feedbacks.extend(db.query(RideFeedback).all())
        except SQLAlchemyError:
            continue

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
def get_vehicles(member_id: int, shards: dict = Depends(get_db_shards)):
    verify_admin(member_id)

    logger.info("Admin Action: Utilizing Scatter Gather Strategy to Fetch All Vehicles")

    vehicles = []
    for shard_num, db in shards.items():
        try:
            vehicles = db.query(Vehicle).all()
            if vehicles: break # Replicated across all shards, so reading from one is enough
        except SQLAlchemyError:
            continue

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
def add_vehicle(member_id: int, vehicle_type: str, max_capacity: int, shards: dict = Depends(get_db_shards)):
    verify_admin(member_id)

    logger.info(f"Admin Action: Replicating Vehicle {vehicle_type} across All DB Shards")

    # Vehicles are small/reference tables and should be replicated entirely across all shards
    vehicle_added_info = None
    for shard_num, db in shards.items():
        try:
            v = Vehicle(VehicleType=vehicle_type, MaxCapacity=max_capacity)
            db.add(v)
            db.commit()
            db.refresh(v)
            if vehicle_added_info is None:
                vehicle_added_info = v
        except SQLAlchemyError as e:
            logger.error(f"Failed to add vehicle to Shard {shard_num}: {e}")

    if not vehicle_added_info:
        raise HTTPException(status_code=500, detail="Failed to add vehicle globally")

    return {"msg": "Vehicle added to all active shards", "VehicleID": vehicle_added_info.VehicleID}