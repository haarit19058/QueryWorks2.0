from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import rides, auth
from database import *
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="IITGN RideShare Portal")

# Centralized CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:3000","http://10.7.59.24:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include both routers
app.include_router(auth.router)
app.include_router(rides.router)

@app.get("/")
def root():
    return {"Message": "Successful Welcome to RideShare Portal"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("VALIDATION ERROR:", exc.errors())   # 👈 prints exact field + reason
    return JSONResponse(status_code=422, content={"detail": exc.errors()})