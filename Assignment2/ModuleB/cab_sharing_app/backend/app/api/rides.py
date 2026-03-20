from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
import uuid

import models
import schemas
import database
from api import auth

router = APIRouter(prefix="/rides", tags=["Rides Management"])

@router.get("/active-rides", response_model=list[schemas.RideFull])
def get_active_rides(db: Session = Depends(database.get_db)):
    rides = db.query(models.ActiveRide).options(
        joinedload(models.ActiveRide.passengers).joinedload(models.RidePassengerMap.member),
        joinedload(models.ActiveRide.admin)  
    ).all()
    
    formatted_rides = []
    for ride in rides:
        # Extract only confirmed passengers and map them to MemberOut schema
        confirmed_passengers = [
            schemas.MemberOut.model_validate(p.member) 
            for p in ride.passengers if p.IsConfirmed and p.member
        ]
        
        # Build the dictionary that strictly matches schemas.RideFull
        ride_dict = {
            "RideID": ride.RideID,
            "AdminID": ride.AdminID,
            "AdminName": ride.admin.FullName if ride.admin else None,
            "AvailableSeats": ride.AvailableSeats,
            "PassengerCount": ride.PassengerCount,
            "Source": ride.Source,
            "Destination": ride.Destination,
            "VehicleType": ride.VehicleType,
            "StartTime": ride.StartTime,
            "EstimatedTime": ride.EstimatedTime,
            "FemaleOnly": ride.FemaleOnly,
            "Passengers": confirmed_passengers
        }
        formatted_rides.append(ride_dict)
        
    return formatted_rides

@router.post("/create-ride", response_model=schemas.RideOut)
def create_ride(ride: schemas.RideCreate, member_id: str = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    new_ride = models.ActiveRide(
        RideID=str(uuid.uuid4()),
        AdminID=member_id,
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

    admin_entry = models.RidePassengerMap(
        RideID=new_ride.RideID, PassengerID=member_id, IsConfirmed=True
    )
    db.add(admin_entry)
    db.commit()
    return new_ride