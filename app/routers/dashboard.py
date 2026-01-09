from datetime import datetime
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from app import models, schemas
from app.dependencies import get_db, get_current_user
from app.services.streaks import compute_streaks_for_daily

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/today", response_model=schemas.DashboardTodayResponse)
def get_today_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        user_tz = ZoneInfo(current_user.timezone or "UTC")
    except Exception:
        user_tz = ZoneInfo("UTC")
    
    now_user_tz = datetime.now(user_tz)
    today = now_user_tz.date()

    habits: List[models.Habit] = (
        db.query(models.Habit)
        .filter(
            models.Habit.user_id == current_user.id,
            models.Habit.is_archived == False,
            models.Habit.start_date <= today,
        )
        .order_by(models.Habit.created_at)
        .all()
    )

    if not habits:
        return schemas.DashboardTodayResponse(date=today, habits=[])
    
    habit_ids = [h.id for h in habits]

    logs: List[models.HabitLog] = (
        db.query(models.HabitLog)
        .filter(
            models.HabitLog.user_id == current_user.id,
            models.HabitLog.habit_id.in_(habit_ids),
            models.HabitLog.date <= today,
        )
        .all()
    )

    logs_by_habit: Dict[int, List[models.HabitLog]] = {hid: [] for hid in habit_ids}
    for log in logs:
        logs_by_habit[log.habit_id].append(log)
    
    items: List[schemas.TodayHabitItem] = []

    for habit in habits:
        habit_logs = logs_by_habit.get(habit.id,[])

        completed_today = any(log.date == today for log in habit_logs)

        log_dates = [log.date for log in habit_logs]
        if habit.goal_type == "DAILY":
            current_streak, best_streak = compute_streaks_for_daily(log_dates, today)
        else:
            current_streak, best_streak = 0, 0
        
        items.append(
            schemas.TodayHabitItem(
                habit=schemas.HabitRead.model_validate(habit),
                is_completed=completed_today,
                current_streak=current_streak,
                best_streak=best_streak
            )
        )

    return schemas.DashboardTodayResponse(date=today, habits=items)
    