import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import declarative_base, relationship

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
    hosted_rides = relationship("ActiveRide", back_populates="admin")
    booking_requests = relationship("BookingRequest", back_populates="passenger")
    messages = relationship("MessageHistory", back_populates="sender")

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
    admin = relationship("Member", back_populates="hosted_rides")
    requests = relationship("BookingRequest", back_populates="ride")
    messages = relationship("MessageHistory", back_populates="ride")

class BookingRequest(Base):
    __tablename__ = "BookingRequests"

    RequestID = Column(Integer, primary_key=True, autoincrement=True)
    RideID = Column(String(50), ForeignKey("ActiveRides.RideID", ondelete="CASCADE"), nullable=False)
    PassengerID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE"), nullable=False)
    RequestStatus = Column(String(20), default='PENDING', nullable=False)
    RequestedAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    ride = relationship("ActiveRide", back_populates="requests")
    passenger = relationship("Member", back_populates="booking_requests")

class MessageHistory(Base):
    __tablename__ = "MessageHistory"

    MessageID = Column(Integer, primary_key=True, autoincrement=True)
    RideID = Column(String(50), ForeignKey("ActiveRides.RideID", ondelete="CASCADE"), nullable=False)
    SenderID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE"), nullable=False)
    MessageText = Column(String(500), nullable=False)
    Timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    IsRead = Column(Boolean, default=False, nullable=False)

    # Relationships
    ride = relationship("ActiveRide", back_populates="messages")
    sender = relationship("Member", back_populates="messages")