# from fastapi import APIRouter, Depends, HTTPException, Header
# from sqlalchemy.orm import Session
# from jose import JWTError, jwt
# from datetime import datetime, timedelta
# from pydantic import BaseModel
# import httpx
# import os
# from dotenv import load_dotenv

# import models
# import database

# load_dotenv()

# router = APIRouter(prefix="/auth", tags=["Authentication"])

# # Use environment variables securely
# SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "fallback-secret-key") 
# ALGORITHM = "HS256"
# CLIENT_ID = os.environ.get("CLIENT_ID")
# CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
# REDIRECT_URI = os.environ.get("REDIRECT_URI", "postmessage")

# class AuthRequest(BaseModel):
#     code: str

# def create_jwt(member_id: int):
#     payload = {
#         "member_id": member_id,
#         "exp": datetime.utcnow() + timedelta(days=7)
#     }
#     return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# def get_current_user(authorization: str = Header(None)):
#     """Dependency to check the token on protected routes"""
#     if not authorization or not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Missing or invalid authentication token")
    
#     token = authorization.split(" ")[1]
    
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload.get("member_id")
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Token has expired or is invalid. Please log in again.")

# @router.post("/login")
# async def google_auth(request: AuthRequest, db: Session = Depends(database.get_db)):
#     # 1. Exchange authorization code for access token
#     token_url = "https://oauth2.googleapis.com/token"
#     data = {
#         "code": request.code,
#         "client_id": CLIENT_ID,
#         "client_secret": CLIENT_SECRET,
#         "redirect_uri": REDIRECT_URI,
#         "grant_type": "authorization_code",
#     }
    
#     async with httpx.AsyncClient() as client:
#         response = await client.post(token_url, data=data)
#         token_data = response.json()
        
#     if "error" in token_data:
#         raise HTTPException(status_code=400, detail=token_data.get("error_description"))

#     # 2. Fetch user info from Google
#     user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
#     async with httpx.AsyncClient() as client:
#         user_info_res = await client.get(
#             user_info_url, 
#             headers={"Authorization": f"Bearer {token_data['access_token']}"}
#         )
#         user_info = user_info_res.json()

#     print(user_info)
#     # 3. Domain Check
#     user_email = user_info.get("email", "")
#     if not user_email.endswith("@iitgn.ac.in"):
#         raise HTTPException(status_code=403, detail="Access restricted to university students only.")

#     google_sub = user_info.get("sub")
#     name = user_info.get("name")

#     # 4. Database Check / User Creation
#     user = db.query(models.Member).filter(models.Member.GoogleSub == google_sub).first()

#     if not user:
#         return {"isNewUser":True, "email": user_email, "name":user_info.get("name"), "picture": user_info.get("picture")}

#     # 5. Create Local JWT
#     access_token = create_jwt(user.MemberID)

#     return {"isNewUser":False, "token": access_token, "user": user_info} 

# @router.post("/signup")

from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, Request
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv
# from ..schemas import SignupRequest
from schemas import SignupRequest 
import uuid
import models
import database

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "fallback-secret-key")
ALGORITHM = "HS256"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "postmessage")

class AuthRequest(BaseModel):
    code: str

# class SignupRequest(BaseModel):
#     google_sub: str
#     email: str
#     name: str
#     picture: str
#     phone: str        
#     # whatever extra fields you collect
#     # add more fields as needed...

def create_jwt(member_id: int):
    payload = {
        "member_id": member_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def set_auth_cookie(response: Response, member_id: int):
    """Helper to avoid repeating cookie config in login + signup"""
    token = create_jwt(member_id)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,          # JS cannot read it
        secure=True,            # HTTPS only (set False for local dev)
        samesite="lax",         # CSRF protection
        max_age=60 * 60 * 24 * 7  # 7 days, matches JWT expiry
    )

def get_current_user(
    session: str | None = Cookie(default=None),  # reads cookie automatically
    db: Session = Depends(database.get_db)
):
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(session, SECRET_KEY, algorithms=[ALGORITHM])
        member_id = payload.get("member_id")
        if not member_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

    user = db.query(models.Member).filter(models.Member.MemberID == member_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/login")
async def google_login(
    request: AuthRequest,
    response: Response,           # 👈 needed to set cookie
    db: Session = Depends(database.get_db)
):
    # 1. Exchange code for access token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": request.code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        token_res = await client.post(token_url, data=data)
        token_data = token_res.json()

    if "error" in token_data:
        raise HTTPException(status_code=400, detail=token_data.get("error_description"))

    # 2. Fetch user info from Google
    async with httpx.AsyncClient() as client:
        user_info_res = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        user_info = user_info_res.json()
    print(user_info)

    # 3. Domain check
    user_email = user_info.get("email", "")
    if not user_email.endswith("@iitgn.ac.in"):
        raise HTTPException(status_code=403, detail="Access restricted to university students only.")

    google_sub = user_info.get("sub")

    # 4. Check if user exists
    user = db.query(models.Member).filter(models.Member.GoogleSub == google_sub).first()

    if not user:
        # New user — send info to frontend, no cookie yet
        # Cookie is only set after they complete signup
        return {
            "isNewUser": True,
            "email": user_email,
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "google_sub": google_sub   # frontend passes this back in /signup
        }

    # 5. Existing user — set cookie and return user info
    set_auth_cookie(response, user.MemberID)    # 👈 cookie set here, not token in body

    return {
        "isNewUser": False,
        "user": {
            "name": user.Name,
            "email": user.Email,
            "picture": user_info.get("picture")
        }
    }


@router.post("/signup")
async def google_signup(
    raw_request: Request,   # 👈 add this temporarily
    request: SignupRequest,
    response: Response,
    db: Session = Depends(database.get_db)
):

    # Guard: don't create duplicate users
    existing = db.query(models.Member).filter(models.Member.GoogleSub == request.google_sub).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists. Please log in.")
    
    for column in models.Member.__table__.columns:
        print(f"{column.name:20} {column.type} nullable={column.nullable}")

    
    # Create new user with the extra details from signup form
    new_user = models.Member(
        GoogleSub=request.google_sub,
        Email=request.Email,                  # was request.email
        FullName=request.FullName,
        ProfileImageURL=request.ProfileImageURL,  # was request.picture
        Programme=request.Programme,
        Branch=request.Branch,
        BatchYear=request.BatchYear,
        ContactNumber=request.ContactNumber,  # was request.phone
        Age=request.Age,
        Gender=request.Gender,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Set cookie now that signup is complete
    set_auth_cookie(response, new_user.MemberID)    # 👈 same helper as login

    return {
        "isNewUser": False,   # they're fully registered now
        "user": {
            "name": new_user.Name,
            "email": new_user.Email,
            "picture": new_user.Picture
        }
    }


@router.get("/me")
def get_me(current_user: models.Member = Depends(get_current_user)):
    """Frontend calls this on app load to restore session"""
    return {
        "name": current_user.Name,
        "email": current_user.Email,
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session")
    return {"message": "Logged out"}