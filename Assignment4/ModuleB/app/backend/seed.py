import uuid
from datetime import datetime, timedelta, timezone, date, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Import all models (Make sure to import the new ones!)
from models import (
    Base, Member, ActiveRide, BookingRequest, MessageHistory, 
    MemberStat, RidePassengerMap, Vehicle, MemberRating, 
    RideFeedback, RideHistory, Cancellation
)

load_dotenv()
DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL", "sqlite:///./rideshare.db") # Fallback for testing
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def seed_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Populate Vehicles (From SQL Dump)
        v1 = Vehicle(VehicleType="Bike", MaxCapacity=1)
        v2 = Vehicle(VehicleType="Auto Rickshaw", MaxCapacity=3)
        v3 = Vehicle(VehicleType="Mini Cab", MaxCapacity=4)
        v4 = Vehicle(VehicleType="Sedan Cab", MaxCapacity=4)
        v5 = Vehicle(VehicleType="SUV Cab", MaxCapacity=6)
        db.add_all([v1, v2, v3, v4, v5])
        db.commit()

        # 2. Populate Members
        m1 = Member(
            GoogleSub="google_sub_123", FullName="Aarav Patel", Email="aarav.p@iitgn.ac.in",
            ProfileImageURL="https://picsum.photos/seed/1/100", Programme="B.Tech", Branch="CSE",
            BatchYear=2026, ContactNumber="9876543210", Age=20, Gender="M"
        )
        m2 = Member(
            GoogleSub="google_sub_456", FullName="Diya Sharma", Email="diya.s@iitgn.ac.in",
            ProfileImageURL="https://picsum.photos/seed/2/100", Programme="B.Tech", Branch="EE",
            BatchYear=2026, ContactNumber="9876543211", Age=20, Gender="F"
        )
        m3 = Member(
            GoogleSub="google_sub_789", FullName="Kabir Singh", Email="kabir.s@iitgn.ac.in",
            ProfileImageURL="https://picsum.photos/seed/3/100", Programme="M.Tech", Branch="ME",
            BatchYear=2025, ContactNumber="9876543212", Age=23, Gender="M"
        )
        db.add_all([m1, m2, m3])
        db.commit()

        # 3. Populate MemberStats
        stat1 = MemberStat(MemberID=m1.MemberID, AverageRating=4.67, TotalRidesTaken=73, TotalRidesHosted=54, NumberOfRatings=146)
        stat2 = MemberStat(MemberID=m2.MemberID, AverageRating=3.43, TotalRidesTaken=99, TotalRidesHosted=1, NumberOfRatings=198)
        db.add_all([stat1, stat2])
        db.commit()

        # 4. Populate ActiveRides
        now = datetime.now(timezone.utc)
        r1 = ActiveRide(
            AdminID=m1.MemberID, AvailableSeats=2, PassengerCount=2, 
            Source="IIT Gandhinagar (Palaj)", Destination="Ahmedabad Airport (AMD)",
            VehicleType="SUV Cab", StartTime=now + timedelta(days=1), EstimatedTime=45, 
            FemaleOnly=False, Status="ACTIVE"
        )
        r2 = ActiveRide(
            AdminID=m2.MemberID, AvailableSeats=3, PassengerCount=1, 
            Source="Gift City", Destination="IIT Gandhinagar (Palaj)",
            VehicleType="Auto Rickshaw", StartTime=now + timedelta(hours=5), EstimatedTime=30, 
            FemaleOnly=True, Status="ACTIVE"
        )
        db.add_all([r1, r2])
        db.commit()

        # 5. Populate RidePassengerMap
        map1 = RidePassengerMap(RideID=r1.RideID, PassengerID=m2.MemberID, IsConfirmed=True)
        db.add(map1)
        db.commit()

        # 6. Populate BookingRequests
        req1 = BookingRequest(RideID=r1.RideID, PassengerID=m2.MemberID, RequestStatus="APPROVED")
        req2 = BookingRequest(RideID=r1.RideID, PassengerID=m3.MemberID, RequestStatus="PENDING")
        db.add_all([req1, req2])
        db.commit()

        # 7. Populate MessageHistory
        msg1 = MessageHistory(RideID=r1.RideID, SenderID=m2.MemberID, MessageText="Where exactly at the housing block?")
        msg2 = MessageHistory(RideID=r1.RideID, SenderID=m1.MemberID, MessageText="Near Block A entrance!")
        db.add_all([msg1, msg2])
        db.commit()

        # 8. Populate RideFeedback & MemberRatings
        feedback1 = RideFeedback(RideID=r1.RideID, MemberID=m2.MemberID, FeedbackText="Felt safe throughout.", FeedbackCategory="Safety")
        rating1 = MemberRating(RideID=r1.RideID, SenderMemberID=m2.MemberID, ReceiverMemberID=m1.MemberID, Rating=4.8, RatingComment="Great ride, very smooth!")
        db.add_all([feedback1, rating1])
        db.commit()

        # 9. Populate RideHistory
        past_ride_id = str(uuid.uuid4())
        history1 = RideHistory(
            RideID=past_ride_id, AdminID=m1.MemberID, RideDate=date(2026, 2, 12),
            StartTime=time(6, 15), Source="Infocity", Destination="IIT Gandhinagar (Palaj)",
            Platform="Ola", Price=196, FemaleOnly=False
        )
        db.add(history1)
        db.commit()

        # 10. Populate Cancellation
        cancellation1 = Cancellation(RideID=r2.RideID, MemberID=m3.MemberID, CancellationReason="Bad co-passengers")
        db.add(cancellation1)
        db.commit()

        print("Database seeded successfully with expanded dummy data!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()