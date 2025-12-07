from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime 
from typing import List, Optional
from enum import Enum

class GoalType(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    X_PER_WEEK = "X_PER_WEEK"

# ------------- USER SCHEMAS -------------------
class UserBase(BaseModel):
    username: str
    email: str
    timezone: str = "UTC"

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    timezone: Optional[str] = None
    password: Optional[str] = None

class UserRead(BaseModel): 

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    timezone: str
    created_at: datetime

# ----------------------- HABIT SCHEMAS ------------------------
class HabitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = ""
    goal_type: GoalType = GoalType.DAILY
    target_per_period: int = Field(default=1, ge=1)
    start_date: date

class HabitCreate(HabitBase):
    pass

class HabitUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    goal_type: Optional[GoalType] = None
    target_per_period: Optional[int] = Field(default=None, ge=1)
    start_date: Optional[date] = None
    is_archived: Optional[bool] = None

class HabitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    description: str
    goal_type: GoalType
    target_per_period: int
    start_date: date
    is_archived: bool
    created_at: datetime

# ------------------ HABIT LOG SCHEMAS --------------------------
class HabitLogBase(BaseModel):
    date: date
    value: int = Field(default=1,ge=0)

class HabitLogCreate(HabitLogBase):
    pass

class HabitLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    habit_id: int
    user_id: int
    date: date
    value: int
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str