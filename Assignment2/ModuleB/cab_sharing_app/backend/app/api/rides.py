from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
import uuid

import models
import schemas
import database
from api import auth

router = APIRouter(
    prefix="/rides",
    tags=["Rides Management"]
)

@router.get("/active-rides", response_model=list[schemas.RideFull])
def get_active_rides(db: Session = Depends(database.get_db)):
    rides = db.query(models.ActiveRide).options(
        joinedload(models.ActiveRide.passengers)
        .joinedload(models.RidePassengerMap.member),
        joinedload(models.ActiveRide.admin)  
    ).all()

    res = []
    for r in rides:
        members = [
            {"MemberID": p.member.MemberID, "FullName": p.member.FullName}
            for p in r.passengers if p.member
        ]

        res.append({
            "RideID": r.RideID,
            "AdminID": r.AdminID,
            "AdminName": r.admin.FullName if r.admin else None, 
            "AvailableSeats": r.AvailableSeats,
            "PassengerCount": r.PassengerCount,
            "Source": r.Source,
            "Destination": r.Destination,
            "VehicleType": r.VehicleType,
            "StartTime": r.StartTime,
            "EstimatedTime": r.EstimatedTime,
            "FemaleOnly": r.FemaleOnly,
            "Passengers": members
        })

    return res

@router.get("/your-rides", response_model=list[schemas.RideFull])
def get_your_rides(
    member_id: int = Depends(auth.get_current_user), 
    db: Session = Depends(database.get_db)
):
    rides = db.query(models.ActiveRide).options(
        joinedload(models.ActiveRide.passengers)
        .joinedload(models.RidePassengerMap.member),
        joinedload(models.ActiveRide.admin)
    ).filter(
        (models.ActiveRide.AdminID == member_id) |
        (models.ActiveRide.passengers.any(
            models.RidePassengerMap.PassengerID == member_id
        ))
    ).all()

    res = []
    for r in rides:
        passengers = [
            {"MemberID": p.member.MemberID, "FullName": p.member.FullName}
            for p in r.passengers if p.member
        ]

        res.append({
            "RideID": r.RideID,
            "AdminID": r.AdminID,
            "AdminName": r.admin.FullName if r.admin else None,
            "AvailableSeats": r.AvailableSeats,
            "PassengerCount": r.PassengerCount,
            "Source": r.Source,
            "Destination": r.Destination,
            "VehicleType": r.VehicleType,
            "StartTime": r.StartTime,
            "EstimatedTime": r.EstimatedTime,
            "FemaleOnly": r.FemaleOnly,
            "Passengers": passengers
        })

    return res

@router.get("/profile/{profile_id}")
def get_profile(profile_id: int, db: Session = Depends(database.get_db)):
    member = db.query(models.Member).filter(
        models.Member.MemberID == profile_id
    ).first()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    stats = db.query(models.MemberStats).filter(
        models.MemberStats.MemberID == profile_id
    ).first()

    return {
        "MemberID": member.MemberID,
        "FullName": member.FullName,
        "Email": member.Email,
        "Programme": member.Programme,
        "Branch": member.Branch,
        "BatchYear": member.BatchYear,
        "ContactNumber": member.ContactNumber,
        "Age": member.Age,
        "Gender": member.Gender,
        "ProfileImageURL": member.ProfileImageURL,

        "Stats": {
            "AverageRating": float(stats.AverageRating) if stats else 0,
            "TotalRidesTaken": stats.TotalRidesTaken if stats else 0,
            "TotalRidesHosted": stats.TotalRidesHosted if stats else 0,
            "NumberOfRatings": stats.NumberOfRatings if stats else 0,
        }
    }

@router.post("/create-ride", response_model=schemas.RideOut)
def create_ride(
    ride: schemas.RideCreate,
    member_id: int = Depends(auth.get_current_user), 
    db: Session = Depends(database.get_db)
):
    new_ride = models.ActiveRide(
        RideID=str(uuid.uuid4()),
        AdminID=member_id,  # Overwrite with authenticated user
        AvailableSeats=ride.AvailableSeats,
        PassengerCount=1,   
        Source=ride.Source,
        Destination=ride.Destination,
        VehicleType=ride.VehicleType,
        StartTime=ride.StartTime,
        EstimatedTime=ride.EstimatedTime,
        FemaleOnly=ride.FemaleOnly
    )

    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    admin = db.query(models.Member).filter(models.Member.MemberID == member_id).first()

    if not admin:
        raise HTTPException(status_code=400, detail="Invalid AdminID")

    admin_entry = models.RidePassengerMap(
        RideID=new_ride.RideID,
        PassengerID=member_id,
        IsConfirmed=True
    )

    db.add(admin_entry)
    db.commit()

    return new_ride

@router.get("/requests/{ride_id}")
def get_requests_by_ride(ride_id: str, db: Session = Depends(database.get_db)):
    data = db.query(models.BookingRequest, models.Member)\
        .join(models.Member, models.Member.MemberID == models.BookingRequest.PassengerID)\
        .filter(models.BookingRequest.RideID == ride_id)\
        .all()

    res = []
    for req, member in data:
        res.append({
            "RequestID": req.RequestID,
            "RideID": req.RideID,
            "PassengerID": req.PassengerID,
            "PassengerName": member.FullName,
            "RequestStatus": req.RequestStatus,
            "RequestedAt": req.RequestedAt
        })

    return res