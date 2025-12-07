from fastapi import FastAPI
from app.routers import auth, habits
from app import models
from app.db import engine

# the method defined here is used to set up the database locally when uvicorn is run
def create_tables_if_not_exist():
    models.Base.metadata.create_all(bind=engine)
create_tables_if_not_exist()
app = FastAPI(
    title="Habit Tracker API"
)

app.include_router(auth.router)
app.include_router(habits.router)
# this is just a default route and can be removed later 
# @app.get("/")
# def hello():
#     return {"message":"Hello FastAPI"}