from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Member, ActiveRide, BookingRequest, MessageHistory


from dotenv import load_dotenv
import os
# Replace with your actual database URL (e.g., mysql+pymysql://user:pass@localhost/RideShare)
load_dotenv()
DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def seed_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Populate Members
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

        # 2. Populate ActiveRides
        now = datetime.now(timezone.utc)
        r1 = ActiveRide(
            AdminID=m1.MemberID, AvailableSeats=2, PassengerCount=2, 
            Source="IITGN Housing Block", Destination="Ahmedabad Airport (AMD)",
            VehicleType="Car", StartTime=now + timedelta(days=1), EstimatedTime=45, 
            FemaleOnly=False, Status="ACTIVE"
        )
        r2 = ActiveRide(
            AdminID=m2.MemberID, AvailableSeats=3, PassengerCount=1, 
            Source="IITGN Academic Block", Destination="Motera Stadium Metro",
            VehicleType="Auto Rickshaw", StartTime=now + timedelta(hours=5), EstimatedTime=30, 
            FemaleOnly=True, Status="ACTIVE"
        )
        db.add_all([r1, r2])
        db.commit()

        # 3. Populate BookingRequests
        req1 = BookingRequest(RideID=r1.RideID, PassengerID=m2.MemberID, RequestStatus="APPROVED")
        req2 = BookingRequest(RideID=r1.RideID, PassengerID=m3.MemberID, RequestStatus="PENDING")
        db.add_all([req1, req2])
        db.commit()

        # 4. Populate MessageHistory
        msg1 = MessageHistory(RideID=r1.RideID, SenderID=m2.MemberID, MessageText="Where exactly at the housing block?")
        msg2 = MessageHistory(RideID=r1.RideID, SenderID=m1.MemberID, MessageText="Near Block A entrance!")
        db.add_all([msg1, msg2])
        db.commit()

        print("Database seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()