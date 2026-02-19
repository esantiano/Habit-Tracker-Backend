from datetime import date, timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from app import models, schemas
from app.dependencies import get_current_user, get_db
from app.services.streaks import compute_streaks_for_daily, compute_streaks_for_x_per_week

router = APIRouter(prefix="/stats", tags=["stats"])

def range_to_dates(range_str: str, today: date):
    mapping = {"7d": 7, "30d": 30, "90d":90}
    days = mapping.get(range_str, 30)
    start = today - timedelta(days=days-1)
    end = today
    return start, end

@router.get("/overview", response_model=schemas.StatsOverviewResponse)
def stats_overview(
    range: str = "30d",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    ):

    try:
        user_tz = ZoneInfo(current_user.timezone or "UTC")
    except Exception:
        user_tz = ZoneInfo("UTC")
    
    now_user_tz = datetime.now(user_tz)
    today = now_user_tz.date()
    start_date, end_date = range_to_dates(range, today)

    habits = db.query(models.Habit).filter(
        models.Habit.user_id == current_user.id,
        models.Habit.is_archived == False,
        models.Habit.start_date <= end_date,
    ).all()

    habit_ids = [h.id for h in habits]
    logs = db.query(models.HabitLog).filter(
        models.HabitLog.user_id == current_user.id,
        models.HabitLog.habit_id.in_(habit_ids),
        models.HabitLog.date >= start_date,
        models.HabitLog.date <= end_date,
    ).all()

    logs_by_habit = {hid: [] for hid in habit_ids}
    for log in logs:
        logs_by_habit[log.habit_id].append(log)

    total_checkins = len(logs)

    habit_stats = []
    total_possible = 0
    total_completed = 0

    days_in_range = (end_date - start_date).days + 1

    for h in habits:
        h_logs = logs_by_habit.get(h.id, [])
        log_dates = [l.date for l in h_logs]

        if h.goal_type == "DAILY":
            current_streak, best_streak = compute_streaks_for_daily(log_dates, today)
            unique_days = len(set(log_dates))
            possible = days_in_range
            completion_rate = unique_days / possible if possible else 0.0

            total_possible += possible
            total_completed += unique_days

            habit_stats.append(schemas.HabitStats(
                habit_id=h.id,
                name=h.name,
                goal_type=h.goal_type,
                target_per_period=h.target_per_period,
                completion_count=unique_days,
                completion_rate=completion_rate,
                current_streak=current_streak,
                best_streak=best_streak,
            ))
        elif h.goal_type == "X_PER_WEEK":
            current_streak, best_streak = compute_streaks_for_x_per_week(
                log_dates, today, h.target_per_period
            )

            completion_count = len(log_dates)
            habit_stats.append(schemas.HabitStats(
                habit_id=h.id,
                name=h.name,
                goal_type=h.goal_type,
                target_per_period=h.target_per_period,
                completion_count=completion_count,
                completion_rate=0.0,
                current_streak=current_streak,
                best_streak=best_streak,
            ))
    
    overall_rate = (total_completed / total_possible) if total_possible else 0.0

    return schemas.StatsOverviewResponse(
        start_date=start_date,
        end_date=end_date,
        total_habits=len(habits),
        active_habits=len(habits),
        total_checkins=total_checkins,
        overall_completion_rate=overall_rate,
        habits=habit_stats
    )