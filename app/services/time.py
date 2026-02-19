from datetime import datetime, date
from zoneinfo import ZoneInfo

def get_today_for_user(user_timezone: str | None) -> date:
    tz_name = user_timezone or "America/New_York"
    try:
        tz = ZoneInfo(tz_name)
    except Exception: 
        tz = ZoneInfo("America/New_York")
    return datetime.now(tz).date()