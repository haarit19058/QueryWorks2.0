import requests as http_requests # Add this to your imports at the top
from fastapi import FastAPI, Depends, HTTPException, Response, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone

from models import Base, Member, ActiveRide, BookingRequest, MessageHistory, MemberStat
from typing import Any

from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL") # Update to your MySQL connection string
GOOGLE_CLIENT_ID = os.environ.get("CLIENT_ID")
JWT_SECRET = os.environ.get("JWT_SECRET_KEY", "fallback-secret-key")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
ALGORITHM = "HS256"

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
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        
        # FIX: Cast the string subject back to an integer for the database
        member_id = int(payload.get("sub")) 
        
        user = db.query(Member).filter(Member.MemberID == member_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.PyJWTError as e:
        print(f"🔥🔥🔥 JWT DECODE ERROR: {e} 🔥🔥🔥") 
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
        print("Google Token Exchange Error:", token_res.json()) # Helpful for debugging
        raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
        
    token_data = token_res.json()
    extracted_id_token = token_data.get("id_token")

    # 2. Verify the ID Token now that we have it
    try:
        from google.auth.transport import requests as google_requests
        idinfo = id_token.verify_oauth2_token(extracted_id_token, google_requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo['email']
        
        if not email.endswith('@iitgn.ac.in'):
            raise HTTPException(status_code=403, detail="Only IITGN emails allowed")

        user = db.query(Member).filter(Member.Email == email).first()
        
        if user:
            create_cookie(response, user.MemberID)
            return {"isNewUser": False, "user": user}
        else:
            return {
                "isNewUser": True,
                "email": email,
                "name": idinfo.get("name"),
                "picture": idinfo.get("picture"),
                "google_sub": idinfo["sub"]
            }
    except ValueError:
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
    create_cookie(response, new_user.MemberID)
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
    print(current_user)
    rides = db.query(ActiveRide).all()
    result = []
    
    for ride in rides:
        # Get host info
        host = db.query(Member).filter(Member.MemberID == ride.AdminID).first()
        
        # Get approved passengers
        approved_reqs = db.query(BookingRequest).filter(
            BookingRequest.RideID == ride.RideID, 
            BookingRequest.RequestStatus == "APPROVED"
        ).all()
        
        passengers = []
        for req in approved_reqs:
            p = db.query(Member).filter(Member.MemberID == req.PassengerID).first()
            if p:
                passengers.append({"MemberID": p.MemberID, "FullName": p.FullName})
        
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
    return new_ride

@app.patch("/rides/{ride_id}/status")
def update_ride_status(ride_id: str, data: UpdateRideStatusData, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    ride = db.query(ActiveRide).filter(ActiveRide.RideID == ride_id, ActiveRide.AdminID == user.MemberID).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found or unauthorized")
    
    ride.Status = data.status
    db.commit()
    return {"message": "Status updated"}

# --- Routes: Bookings ---
# This api is for the AvailableRides page to show the user correct UI
@app.get("/booking-requests")
def get_bookings(db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    # The frontend fetches requests for the current user
    requests = db.query(BookingRequest).filter(BookingRequest.PassengerID == user.MemberID).all()
    return requests

@app.post("/booking-requests")
def request_join(data: RequestJoinData, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    new_req = BookingRequest(RideID=data.RideID, PassengerID=user.MemberID)
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    return new_req

@app.patch("/booking-requests/{request_id}")
def update_booking(request_id: int, data: UpdateRequestData, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    req = db.query(BookingRequest).filter(BookingRequest.RequestID == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Optional: Verify current_user is the Admin of the ride
    req.RequestStatus = data.RequestStatus
    
    if data.RequestStatus == "APPROVED":
        ride = db.query(ActiveRide).filter(ActiveRide.RideID == req.RideID).first()
        if ride and ride.AvailableSeats > 0:
            ride.AvailableSeats -= 1
            ride.PassengerCount += 1
            
    db.commit()
    return {"message": "Request updated"}

# --- Routes: Messages ---
@app.get("/messages")
def get_messages(rideId: str, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    messages = db.query(MessageHistory).filter(MessageHistory.RideID == rideId).order_by(MessageHistory.Timestamp.asc()).all()
    
    result = []
    for msg in messages:
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