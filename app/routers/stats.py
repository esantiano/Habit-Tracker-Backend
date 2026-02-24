from datetime import date, timedelta, datetime
from typing import Dict, List, Set
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from app import models, schemas
from app.dependencies import get_current_user, get_db
from app.services.streaks import compute_streaks_for_daily, compute_streaks_for_x_per_week
from app.services.time import get_today_for_user

router = APIRouter(prefix="/stats", tags=["stats"])

def week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())

def range_to_dates(range_str: str, today: date):
    mapping = {"7d": 7, "30d": 30, "90d":90}
    days = mapping.get(range_str, 30)
    start = today - timedelta(days=days-1)
    end = today
    return start, end

def user_today(user_tz_name: str | None) -> date:
    tz_name = user_tz_name or "America/New_York"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("America/New_York")
    return datetime.now(tz).date()

@router.get("/heatmap", response_model=schemas.HeatmapResponse)
def heatmap(
    range: str = Query("365d", pattern="^(7d|30d|90d|180d|365d)$"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    today = user_today(current_user.timezone)
    start_date, end_date = range_to_dates(range, today)

    logs: List[models.HabitLog] = (
        db.query(models.HabitLog)
        .filter(
            models.HabitLog.user_id == current_user.id,
            models.HabitLog.date >= start_date,
            models.HabitLog.date <= end_date,
        )
        .all()
    )

    count_by_day: Dict[date, int] = {}
    for log in logs:
        count_by_day[log.date] = count_by_day.get(log.date, 0) + 1
    
    days: List[schemas.HeatmapDay] = []
    d = start_date
    while d <= end_date:
        count = count_by_day.get(d, 0)
        days.append(schemas.HeatmapDay(date=d, count=count))
        d += timedelta(days=1)
    
    return schemas.HeatmapResponse(start_date=start_date, end_date=end_date, days=days)

@router.get("/consistency", response_model=schemas.ConsistencyScoreResponse)
def consistency_score(
    range: str = Query("30d", pattern="^(7d|30d|90d|180d|365d)$"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
): 
    today = user_today(current_user.timezone)
    start_date, end_date = range_to_dates(range, today)

    habits = (
        db.query(models.Habit)
        .filter(
            models.Habit.user_id == current_user.id,
            models.Habit.is_archived == False,
            models.Habit.start_date <= end_date,
        )
        .all()
    )
    
    if not habits:
        return schemas.ConsistencyScoreResponse(
            start_date=start_date,
            end_date=end_date,
            score=0.0,
            successful_periods=0,
            total_periods=0,
        )
    
    habit_ids = [h.id for h in habits]
    
    logs = (
        db.query(models.HabitLog)
        .filter(
            models.HabitLog.user_id == current_user.id,
            models.HabitLog.habit_id.in_(habit_ids),
            models.HabitLog.date >= start_date,
            models.HabitLog.date <= end_date,
        )
        .all()
    )

    log_dates_by_habit: Dict[int, list[date]] = {hid: [] for hid in habit_ids}
    for log in logs:
        log_dates_by_habit[log.habit_id].append(log.date)
    
    successful = 0
    total = 0

    days_in_range = (end_date - start_date).days + 1

    for h in habits:
        log_dates = log_dates_by_habit.get(h.id, [])

        if h.goal_type == "DAILY":
            effective_start = max(start_date, h.start_date)
            possible_days = (end_date - effective_start).days + 1 if effective_start <= end_date else 0
            if possible_days <= 0:
                continue
        
            completed_days = len({d for d in log_dates if effective_start <= d <= end_date})
            successful += completed_days
            total += possible_days
        
        elif h.goal_type == "X_PER_WEEK":
            effective_start = max(start_date, h.start_date)
            ws_start = week_start(effective_start)
            ws_end = week_start(end_date)
            weeks_in_range = ((ws_end - ws_start).days // 7) + 1 if ws_start <= ws_end else 0
            if weeks_in_range <= 0:
                continue
            
            counts: Dict[date, int] = {}
            for d in log_dates:
                ws = week_start(d)
                if ws_start <= ws <= ws_end:
                    counts[ws] = counts.get(ws, 0) + 1
                
                successful_weeks = sum(1 for ws, c in counts.items() if c >= h.target_per_period)
                successful += successful_weeks
                total += weeks_in_range

    score = (successful / total * 100.0) if total else 0.0 

    return schemas.ConsistencyScoreResponse(
        start_date=start_date,
        end_date=end_date,
        score=score,
        successful_periods=successful,
        total_periods=total,
    )

@router.get("/overview", response_model=schemas.StatsOverviewResponse)
def stats_overview(
    range: str = "30d",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    ):

    today = get_today_for_user(current_user.timezone)
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

            counts: dict[date, int] = {}
            for d in log_dates:
                ws = week_start(d)
                counts[ws] = counts.get(ws, 0) + 1
            
            range_ws_end = week_start(end_date)

            effective_start = max(start_date, h.start_date)
            eff_ws_start = week_start(effective_start)

            weeks_in_range = ((range_ws_end - eff_ws_start).days // 7) + 1 if eff_ws_start <= range_ws_end else 0

            successful_weeks = sum(
                1 for ws, c in counts.items()
                if ws >= eff_ws_start and ws <= range_ws_end and c >= h.target_per_period
            )

            completion_count = successful_weeks
            completion_rate = (successful_weeks / weeks_in_range) if weeks_in_range else 0.0

            total_possible += weeks_in_range
            total_completed += successful_weeks

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