from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, habits, dashboard, stats
from app import models
from app.db import engine
import os


# the method defined here is used to set up the database locally when uvicorn is run
#def create_tables_if_not_exist():
    #if os.getenv("ENV") != "test":
        #models.Base.metadata.create_all(bind=engine)
#create_tables_if_not_exist()
app = FastAPI(
    title="Habit Tracker API"
)

app.include_router(auth.router)
app.include_router(habits.router)
app.include_router(dashboard.router)
app.include_router(stats.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# this is just a default route and can be removed later 
@app.get("/")
def hello():
    return {"message":"Hello, these are the endpoints for Habit-Tracker-Backend"}