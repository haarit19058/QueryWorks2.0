from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal

class RideBase(BaseModel):
    Source: str
    Destination: str
    StartTime: datetime
    AvailableSeats: int
    VehicleType: str
    FemaleOnly: bool = False

class RideCreate(RideBase):
    EstimatedTime: int
    # ❌ AdminID removed here! The router will securely grab this from the auth token instead.

class RideOut(RideBase):
    RideID: str
    AdminID: str  # ✅ Changed from int to str (UUID)
    
    class Config:
        from_attributes = True

class MemberOut(BaseModel):
    MemberID: str  # ✅ Changed from int to str (UUID)
    FullName: str
    
    class Config:
        from_attributes = True

class RideFull(BaseModel):
    RideID: str
    AdminID: str  # ✅ Changed from int to str (UUID)
    AdminName: str | None  
    AvailableSeats: int
    PassengerCount: int
    Source: str
    Destination: str
    VehicleType: str
    StartTime: datetime
    EstimatedTime: int
    FemaleOnly: bool
    
    Passengers: list[MemberOut]
    
    class Config:
        from_attributes = True
        orm_mode = True

# ---------------------------------------------------------
# NEW SCHEMAS ADDED FOR THE ONBOARDING & REQUESTS PIPELINE
# ---------------------------------------------------------

class ProfileCreate(BaseModel):
    """Used when Google Auth succeeds but the user isn't in our DB yet"""
    GoogleSub: str
    Email: str
    FullName: str
    Programme: str
    Branch: str
    BatchYear: int
    ContactNumber: str
    Age: int
    Gender: str
    ProfileImageURL: Optional[str] = "default_avatar.png"

class RequestAction(BaseModel):
    """Used by the admin to accept or reject a ride request"""
    Action: Literal["ACCEPT", "REJECT"]

class MessageCreate(BaseModel):
    """Used for in-ride group chat"""
    MessageText: str