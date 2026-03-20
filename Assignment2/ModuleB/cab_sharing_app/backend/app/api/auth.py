from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

import models
import database
import schemas

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "fallback-secret-key") 
ALGORITHM = "HS256"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "postmessage")

class AuthRequest(BaseModel):
    code: str

def create_jwt(member_id: str):
    payload = {
        "member_id": member_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authentication token")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("member_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token has expired or is invalid.")



@router.post("/login")
async def google_auth(request: AuthRequest, db: Session = Depends(database.get_db)):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": request.code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        token_data = response.json()
        
    if "error" in token_data:
        raise HTTPException(status_code=400, detail=token_data.get("error_description"))

    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    async with httpx.AsyncClient() as client:
        user_info_res = await client.get(
            user_info_url, 
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        user_info = user_info_res.json()

    user_email = user_info.get("email", "")
    if not user_email.endswith("@iitgn.ac.in"):
        raise HTTPException(status_code=403, detail="Access restricted to university students only.")

    google_sub = user_info.get("sub")
    
    user = db.query(models.Member).filter(models.Member.GoogleSub == google_sub).first()

    # If user doesn't exist, tell frontend to show the "Complete Profile" form
    if not user:
        return {
            "status": "requires_profile_completion", 
            "google_sub": google_sub, 
            "email": user_email, 
            "name": user_info.get("name")
        }
    access_token = create_jwt(user.MemberID)
    return {"status": "success", "token": access_token, "user": user_info}

@router.post("/complete-profile")
def complete_profile(profile: schemas.ProfileCreate, db: Session = Depends(database.get_db)):
    # Check if user somehow already exists
    existing = db.query(models.Member).filter(models.Member.GoogleSub == profile.GoogleSub).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists.")
        
    new_user = models.Member(**profile.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Initialize their stats
    new_stats = models.MemberStats(MemberID=new_user.MemberID)
    db.add(new_stats)
    db.commit()

    access_token = create_jwt(new_user.MemberID)
    return {"status": "success", "token": access_token}