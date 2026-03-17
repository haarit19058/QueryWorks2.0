from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
import database
from api import auth

router = APIRouter(prefix="/requests", tags=["Booking Requests"])

@router.post("/{request_id}/respond")
def respond_to_request(
    request_id: int, 
    action: schemas.RequestAction, 
    admin_id: str = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Admin uses this to ACCEPT or REJECT a pending request."""
    req = db.query(models.BookingRequest).filter(models.BookingRequest.RequestID == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    ride = db.query(models.ActiveRide).filter(models.ActiveRide.RideID == req.RideID).first()
    if ride.AdminID != admin_id:
        raise HTTPException(status_code=403, detail="Only the ride admin can accept/reject requests")

    if req.RequestStatus != "PENDING":
        raise HTTPException(status_code=400, detail=f"Request already {req.RequestStatus}")

    if action.Action == "ACCEPT":
        if ride.AvailableSeats <= 0:
            raise HTTPException(status_code=400, detail="No seats available")
        
        req.RequestStatus = "ACCEPTED"
        ride.AvailableSeats -= 1
        ride.PassengerCount += 1
        
        new_passenger = models.RidePassengerMap(
            RideID=ride.RideID,
            PassengerID=req.PassengerID,
            IsConfirmed=True
        )
        db.add(new_passenger)
        
        system_msg = models.MessageHistory(
            RideID=ride.RideID,
            SenderID=admin_id, 
            MessageText=f"System: A new passenger has joined the ride!"
        )
        db.add(system_msg)

    elif action.Action == "REJECT":
        req.RequestStatus = "REJECTED"

    db.commit()
    return {"message": f"Request {action.Action}ED successfully"}

@router.get("/my-requests")
def get_my_requests(
    passenger_id: str = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Users poll this to see if their requests were ACCEPTED, REJECTED, or are still PENDING."""
    requests = db.query(models.BookingRequest).filter(
        models.BookingRequest.PassengerID == passenger_id
    ).all()
    
    response_data = []
    for req in requests:
        ride = db.query(models.ActiveRide).filter(models.ActiveRide.RideID == req.RideID).first()
        
        if ride:
            response_data.append({
                "RequestID": req.RequestID,
                "RideID": req.RideID,
                "Destination": ride.Destination,
                "Source": ride.Source,
                "StartTime": ride.StartTime,
                "RequestStatus": req.RequestStatus, 
                "RequestedAt": req.RequestedAt
            })
            
    return response_data