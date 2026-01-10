from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_current_user, get_db

router = APIRouter(prefix="/habits", tags=["habits"])

# ----------------- HABIT CRUD ----------------------

@router.get("/", response_model=List[schemas.HabitRead])
def list_habits(
    include_archived: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    q = db.query(models.Habit).filter(models.Habit.user_id == current_user.id)
    
    if not include_archived:
        q = q.filter(models.Habit.is_archived == False)

    habits = q.order_by(models.Habit.created_at).all()

    return habits

@router.post("/", response_model=schemas.HabitRead, status_code=status.HTTP_201_CREATED)
def create_habit(
    habit_in: schemas.HabitCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    habit = models.Habit(
        user_id=current_user.id,
        **habit_in.model_dump()
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit

@router.get("/{habit_id}", response_model=schemas.HabitRead)
def get_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    habit = (
        db.query(models.Habit)
        .filter(models.Habit.id == habit_id, models.Habit.user_id == current_user.id)
        .first()
    )
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    return habit

@router.patch("/{habit_id}", response_model=schemas.HabitRead)
def update_habit(
    habit_id: int,
    habit_in: schemas.HabitUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    habit = (
        db.query(models.Habit)
        .filter(models.Habit.id == habit_id, models.Habit.user_id == current_user.id)
        .first()
    )
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    
    update_data = habit_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)
    
    db.commit()
    db.refresh(habit)
    return habit

@router.patch("/{habit_id}/restore", response_model=schemas.HabitRead)
def restore_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    habit = (
        db.query(models.Habit)
        .filter(models.Habit.id == habit_id, models.Habit.user_id == current_user.id)
        .first()
    )
    if not habit:
        raise HTTPException(status_cod=404, detail="Habit not found")
    
    habit.is_archived = False
    db.commit()
    db.refresh(habit)
    return habit

@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    habit = (
        db.query(models.Habit)
        .filter(models.Habit.id == habit_id, models.Habit.user_id == current_user.id)
        .first()
    )
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    
    habit.is_archived = True
    db.commit()
    return

# ------------------- HABIT LOGS ---------------------------
@ router.get("/{habit_id}/logs", response_model=List[schemas.HabitLogRead])
def get_habit_logs(
    habit_id: int,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    habit = (
        db.query(models.Habit)
        .filter(models.Habit.id == habit_id,)
    )
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    
    q = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.user_id == current_user.id,
    )

    if from_date:
        q = q.filter(models.HabitLog.date>= from_date)
    if to_date:
        q = q.filter(models.HabitLog.date<= to_date)

    logs = q.order_by(models.HabitLog.date).all()
    return logs 

@router.post("/{habit_id}/logs", response_model=schemas.HabitLogRead, status_code=status.HTTP_201_CREATED)
def create_habit_log(
    habit_id: int,
    log_in: schemas.HabitLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    habit = (
        db.query(models.Habit)
        .filter(models.Habit.id == habit_id, models.Habit.user_id == current_user.id)
        .first()
    )
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    
    existing = (
        db.query(models.HabitLog)
        .filter(
            models.HabitLog.habit_id == habit_id,
            models.HabitLog.user_id == current_user.id,
            models.HabitLog.created_at == log_in.date,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Log already exists for this date."
        )

    log = models.HabitLog(
        habit_id=habit_id,
        user_id=current_user.id,
        **log_in.model_dump(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log