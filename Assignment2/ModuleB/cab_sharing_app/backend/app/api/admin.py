from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import database

router = APIRouter(prefix="/admin-superpower", tags=["Admin Superpowers"])

@router.get("/all-users")
def get_all_users(db: Session = Depends(database.get_db)):
    """SUPERPOWER 1: View all user details."""
    return db.query(models.Member).all()

@router.get("/system-stats")
def get_system_stats(db: Session = Depends(database.get_db)):
    """SUPERPOWER 2: See total rides, total users, and total requests."""
    return {
        "TotalUsers": db.query(models.Member).count(),
        "ActiveRides": db.query(models.ActiveRide).count(),
        "TotalCompletedRides": db.query(models.RideHistory).count(),
        "TotalPendingRequests": db.query(models.BookingRequest).filter(models.BookingRequest.RequestStatus == "PENDING").count()
    }

@router.delete("/nuke-ride/{ride_id}")
def force_delete_ride(ride_id: str, db: Session = Depends(database.get_db)):
    """SUPERPOWER 3: Force delete any ride and its traces."""
    db.query(models.RidePassengerMap).filter(models.RidePassengerMap.RideID == ride_id).delete()
    db.query(models.BookingRequest).filter(models.BookingRequest.RideID == ride_id).delete()
    db.query(models.MessageHistory).filter(models.MessageHistory.RideID == ride_id).delete()
    db.query(models.ActiveRide).filter(models.ActiveRide.RideID == ride_id).delete()
    db.commit()
    return {"message": f"Ride {ride_id} successfully wiped."}

@router.post("/override-capacity/{ride_id}")
def override_ride_capacity(ride_id: str, new_capacity: int, db: Session = Depends(database.get_db)):
    """SUPERPOWER 4: Override max capacity limits on an active ride."""
    ride = db.query(models.ActiveRide).filter(models.ActiveRide.RideID == ride_id).first()
    ride.AvailableSeats = new_capacity
    db.commit()
    return {"message": f"Ride {ride_id} capacity overridden to {new_capacity}."}

@router.get("/platform-economy")
def get_platform_economy(db: Session = Depends(database.get_db)):
    """SUPERPOWER 5: See total money exchanged on the platform (Sum of Price in RideHistory)."""
    total_revenue = db.query(func.sum(models.RideHistory.Price)).scalar()
    return {"TotalPlatformEconomy": total_revenue or 0}

@router.get("/all-feedback")
def read_all_feedback(db: Session = Depends(database.get_db)):
    """SUPERPOWER 6: Read raw feedback from everyone."""
    return db.query(models.RideFeedback).order_by(models.RideFeedback.SubmittedAt.desc()).all()