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

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Use environment variables securely
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "fallback-secret-key") 
ALGORITHM = "HS256"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "postmessage")

class AuthRequest(BaseModel):
    code: str

def create_jwt(member_id: int):
    payload = {
        "member_id": member_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(authorization: str = Header(None)):
    """Dependency to check the token on protected routes"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authentication token")
    
    token = authorization.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("member_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token has expired or is invalid. Please log in again.")

@router.post("/login")
async def google_auth(request: AuthRequest, db: Session = Depends(database.get_db)):
    # 1. Exchange authorization code for access token
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

    # 2. Fetch user info from Google
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    async with httpx.AsyncClient() as client:
        user_info_res = await client.get(
            user_info_url, 
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        user_info = user_info_res.json()

    # 3. Domain Check
    user_email = user_info.get("email", "")
    if not user_email.endswith("@iitgn.ac.in"):
        raise HTTPException(status_code=403, detail="Access restricted to university students only.")

    google_sub = user_info.get("sub")
    name = user_info.get("name")

    # 4. Database Check / User Creation
    user = db.query(models.Member).filter(models.Member.GoogleSub == google_sub).first()

    if not user:
        return {"isNewUser":True, "email": user_email, "name":user_info.get("name"), "picture": user_info.get("picture")}

    # 5. Create Local JWT
    access_token = create_jwt(user.MemberID)

    return {"isNewUser":False, "token": access_token, "user": user_info}