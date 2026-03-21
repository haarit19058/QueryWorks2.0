import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Date, Time
from sqlalchemy.orm import declarative_base, relationship
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

Base = declarative_base()

class Member(Base):
    __tablename__ = "Members"

    MemberID = Column(Integer, primary_key=True, autoincrement=True)
    GoogleSub = Column(String(255), unique=True, index=True, nullable=False) # Added for OAuth
    FullName = Column(String(100), nullable=False)
    ProfileImageURL = Column(String(255), default='default_avatar.png')
    Programme = Column(String(50), nullable=False)
    Branch = Column(String(50), nullable=True)
    BatchYear = Column(Integer, nullable=False)
    Email = Column(String(100), unique=True, nullable=False)
    ContactNumber = Column(String(15), unique=True, nullable=False)
    Age = Column(Integer, nullable=True)
    Gender = Column(String(1), nullable=True)

    # Relationships
    hosted_rides = relationship("ActiveRide", passive_deletes=True, back_populates="admin")
    booking_requests = relationship("BookingRequest", passive_deletes=True, back_populates="passenger")
    messages = relationship("MessageHistory",passive_deletes=True, back_populates="sender")

class ActiveRide(Base):
    __tablename__ = "ActiveRides"

    RideID = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    AdminID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE"), nullable=False)
    AvailableSeats = Column(Integer, nullable=False)
    PassengerCount = Column(Integer, nullable=False, default=1)
    Source = Column(String(100), nullable=False)
    Destination = Column(String(100), nullable=False)
    VehicleType = Column(String(30), nullable=False)
    StartTime = Column(DateTime, nullable=False)
    EstimatedTime = Column(Integer, nullable=False)
    FemaleOnly = Column(Boolean, default=False)
    Status = Column(String(20), default="ACTIVE") # Added for standard state management

    # Relationships
    admin = relationship("Member", passive_deletes=True, back_populates="hosted_rides")
    requests = relationship("BookingRequest", passive_deletes=True, back_populates="ride")
    messages = relationship("MessageHistory", passive_deletes=True, back_populates="ride")

class BookingRequest(Base):
    __tablename__ = "BookingRequests"

    RequestID = Column(Integer, primary_key=True, autoincrement=True)
    RideID = Column(String(50), ForeignKey("ActiveRides.RideID", ondelete="CASCADE"), nullable=False)
    PassengerID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE"), nullable=False)
    RequestStatus = Column(String(20), default='PENDING', nullable=False)
    RequestedAt = Column(DateTime, default=lambda: datetime.now(IST), nullable=False)

    # Relationships
    ride = relationship("ActiveRide", back_populates="requests")
    passenger = relationship("Member", back_populates="booking_requests")

class MessageHistory(Base):
    __tablename__ = "MessageHistory"

    MessageID = Column(Integer, primary_key=True, autoincrement=True)
    RideID = Column(String(50), ForeignKey("ActiveRides.RideID", ondelete="CASCADE"), nullable=False)
    SenderID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE"), nullable=False)
    MessageText = Column(String(500), nullable=False)
    Timestamp = Column(DateTime, default=lambda: datetime.now(IST), nullable=False)
    IsRead = Column(Boolean, default=False, nullable=False)

    # Relationships
    ride = relationship("ActiveRide", back_populates="messages")
    sender = relationship("Member", back_populates="messages")

class MemberStat(Base):
    __tablename__ = "MemberStats"

    MemberID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    AverageRating = Column(Float, nullable=False, default=0.00)
    TotalRidesTaken = Column(Integer, nullable=False, default=0)
    TotalRidesHosted = Column(Integer, nullable=False, default=0)
    NumberOfRatings = Column(Integer, nullable=False, default=0)

class RidePassengerMap(Base):
    __tablename__ = "RidePassengerMap"

    # RideID = Column(String(50), ForeignKey("ActiveRides.RideID", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    RideID      = Column(String(50), primary_key=True)
    PassengerID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    IsConfirmed = Column(Boolean, nullable=False, default=True)

class Vehicle(Base):
    __tablename__ = "Vehicles"

    VehicleID = Column(Integer, primary_key=True, autoincrement=True)
    VehicleType = Column(String(30), nullable=False)
    MaxCapacity = Column(Integer, nullable=False)

class MemberRating(Base):
    __tablename__ = "MemberRatings"

    RideID = Column(String(50), primary_key=True)
    SenderMemberID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    ReceiverMemberID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    Rating = Column(Float, nullable=False)
    RatingComment = Column(String(500))
    RatedAt = Column(DateTime, default=lambda: datetime.now(IST), nullable=False)

class RideFeedback(Base):
    __tablename__ = "RideFeedback"

    RideID = Column(String(50), primary_key=True)
    MemberID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    FeedbackText = Column(String(500), nullable=False)
    FeedbackCategory = Column(String(50))
    SubmittedAt = Column(DateTime, default=lambda: datetime.now(IST), nullable=False)

class RideHistory(Base):
    __tablename__ = "RideHistory"

    RideID = Column(String(50), primary_key=True)
    AdminID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    RideDate = Column(Date, nullable=False)
    StartTime = Column(Time, nullable=False)
    Source = Column(String(100), nullable=False)
    Destination = Column(String(100), nullable=False)
    Platform = Column(String(30), nullable=False)
    Price = Column(Integer, nullable=False)
    FemaleOnly = Column(Boolean)

class Cancellation(Base):
    __tablename__ = "Cancellation"

    CancellationID = Column(Integer, primary_key=True, autoincrement=True) # Surrogate key for SQLAlchemy
    RideID = Column(String(50), ForeignKey("ActiveRides.RideID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    MemberID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    CancellationReason = Column(String(255), nullable=False)