from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
import database
from api import auth

router = APIRouter(prefix="/messages", tags=["In-Ride Messaging"])

@router.post("/{ride_id}")
def send_message(
    ride_id: str, 
    msg: schemas.MessageCreate,
    sender_id: str = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Verify user is in the ride
    is_passenger = db.query(models.RidePassengerMap).filter(
        models.RidePassengerMap.RideID == ride_id,
        models.RidePassengerMap.PassengerID == sender_id,
        models.RidePassengerMap.IsConfirmed == True
    ).first()
    
    if not is_passenger:
        raise HTTPException(status_code=403, detail="You are not part of this ride.")

    new_msg = models.MessageHistory(
        RideID=ride_id,
        SenderID=sender_id,
        MessageText=msg.MessageText
    )
    db.add(new_msg)
    db.commit()
    return {"message": "Sent"}

@router.get("/{ride_id}")
def get_messages(ride_id: str, db: Session = Depends(database.get_db)):
    return db.query(models.MessageHistory).filter(models.MessageHistory.RideID == ride_id).order_by(models.MessageHistory.Timestamp.asc()).all()