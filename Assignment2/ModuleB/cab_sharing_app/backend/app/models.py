from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, Boolean, Date, Time, CheckConstraint
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import database

Base = database.Base

class Member(Base):
    __tablename__ = "Members"
    # Updated to String(36) for UUID
    MemberID = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    GoogleSub = Column(String(255), unique=True, nullable=True)
    FullName = Column(String(100), nullable=False)
    ProfileImageURL = Column(String(255), default="default_avatar.png")
    Programme = Column(String(50), nullable=False)
    Branch = Column(String(50))
    BatchYear = Column(Integer, nullable=False)
    Email = Column(String(100), unique=True, nullable=False)
    ContactNumber = Column(String(15), unique=True, nullable=False)
    Age = Column(Integer)
    Gender = Column(String(1))

class MemberStats(Base):
    __tablename__ = "MemberStats"
    MemberID = Column(String(36), ForeignKey("Members.MemberID"), primary_key=True)
    AverageRating = Column(Numeric(3,2), default=0.00)
    TotalRidesTaken = Column(Integer, default=0)
    TotalRidesHosted = Column(Integer, default=0)
    NumberOfRatings = Column(Integer, default=0)

class ActiveRide(Base):
    __tablename__ = "ActiveRides"
    RideID = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    AdminID = Column(String(36), ForeignKey("Members.MemberID"))
    AvailableSeats = Column(Integer, nullable=False)
    PassengerCount = Column(Integer, nullable=False)
    Source = Column(String(100), nullable=False)
    Destination = Column(String(100), nullable=False)
    VehicleType = Column(String(30), nullable=False)
    StartTime = Column(DateTime, nullable=False)
    EstimatedTime = Column(Integer, nullable=False)
    FemaleOnly = Column(Boolean, default=False)
    
    admin = relationship("Member")
    passengers = relationship("RidePassengerMap", back_populates="ride") 

    __table_args__ = (
        CheckConstraint('AvailableSeats >= 0'),
        CheckConstraint('PassengerCount >= 1'),
    )

class Vehicle(Base):
    __tablename__ = "Vehicles"
    VehicleID = Column(Integer, primary_key=True, autoincrement=True)
    VehicleType = Column(String(30), nullable=False)
    MaxCapacity = Column(Integer, nullable=False)

class MessageHistory(Base):
    __tablename__ = "MessageHistory"
    MessageID = Column(Integer, primary_key=True, autoincrement=True)
    RideID = Column(String(50), ForeignKey("ActiveRides.RideID"))
    SenderID = Column(String(36), ForeignKey("Members.MemberID"))
    MessageText = Column(Text, nullable=False)
    Timestamp = Column(DateTime, default=datetime.utcnow)
    IsRead = Column(Boolean, default=False)

class MemberRating(Base):
    __tablename__ = "MemberRatings"
    RideID = Column(String(50), primary_key=True)
    SenderMemberID = Column(String(36), ForeignKey("Members.MemberID"), primary_key=True)
    ReceiverMemberID = Column(String(36), ForeignKey("Members.MemberID"), primary_key=True)
    Rating = Column(Numeric(2,1), nullable=False)
    RatingComment = Column(String(500))
    RatedAt = Column(DateTime, default=datetime.utcnow)

class RideFeedback(Base):
    __tablename__ = "RideFeedback"
    RideID = Column(String(50), primary_key=True)
    MemberID = Column(String(36), ForeignKey("Members.MemberID"))
    FeedbackText = Column(Text, nullable=False)
    FeedbackCategory = Column(String(50))
    SubmittedAt = Column(DateTime, default=datetime.utcnow)

class RideHistory(Base):
    __tablename__ = "RideHistory"
    RideID = Column(String(50), primary_key=True)
    AdminID = Column(String(36), ForeignKey("Members.MemberID"))
    RideDate = Column(Date)
    StartTime = Column(Time)
    Source = Column(String(100))
    Destination = Column(String(100))
    Platform = Column(String(30))
    Price = Column(Integer)
    FemaleOnly = Column(Boolean)

class Cancellation(Base):
    __tablename__ = "Cancellation"
    RideID = Column(String(50), ForeignKey("ActiveRides.RideID"), primary_key=True)
    MemberID = Column(String(36), ForeignKey("Members.MemberID"), primary_key=True)
    CancellationReason = Column(String(255))

class BookingRequest(Base):
    __tablename__ = "BookingRequests"
    RequestID = Column(Integer, primary_key=True, autoincrement=True)
    RideID = Column(String(50), ForeignKey("ActiveRides.RideID"))
    PassengerID = Column(String(36), ForeignKey("Members.MemberID"))
    RequestStatus = Column(String(20), default="PENDING")
    RequestedAt = Column(DateTime, default=datetime.utcnow)

class RidePassengerMap(Base):
    __tablename__ = "RidePassengerMap"
    RideID = Column(String(50), ForeignKey("ActiveRides.RideID"), primary_key=True)
    PassengerID = Column(String(36), ForeignKey("Members.MemberID"), primary_key=True)
    IsConfirmed = Column(Boolean, default=False)
    
    ride = relationship("ActiveRide", back_populates="passengers")
    member = relationship("Member")