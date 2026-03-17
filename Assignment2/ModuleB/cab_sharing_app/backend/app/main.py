from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all your new modular routers
from api import rides, auth, requests, messages, admin

app = FastAPI(title="IITGN RideShare Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount them!
app.include_router(auth.router)
app.include_router(rides.router)
app.include_router(requests.router)
app.include_router(messages.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"Message": "Successful Welcome to RideShare Portal"}