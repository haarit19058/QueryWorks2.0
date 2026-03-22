from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RideBase(BaseModel):
    Source: str
    Destination: str
    StartTime: datetime
    AvailableSeats: int
    VehicleType: str
    FemaleOnly: bool = False

class RideCreate(RideBase):
    AdminID: int
    EstimatedTime: int

class RideOut(RideBase):
    RideID: str
    AdminID: int
    
    class Config:
        from_attributes = True

class MemberOut(BaseModel):
    MemberID: int
    FullName: str

    class Config:
        from_attributes = True

class SignupRequest(BaseModel):
    google_sub: str
    FullName: str
    Email: str                                    # was 'email'
    ProfileImageURL: str = "default_avatar.png"   # was 'picture'
    Programme: str
    Branch: str | None = None
    BatchYear: int
    ContactNumber: str                            # was 'phone'
    Age: int | None = None
    Gender: str | None = None
    # 'name' is gone — FullName replaces it

class RideFull(BaseModel):
    RideID: str
    AdminID: int
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