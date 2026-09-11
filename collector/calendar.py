"""Trading-session helpers. Holiday calendars are configurable until a verified source is chosen."""
from datetime import date, time, datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")


def is_weekday(day: date) -> bool:
    return day.weekday() < 5


def session_for(day: date):
    if not is_weekday(day):
        return []
    return [(datetime.combine(day, time(9, 30), TZ), datetime.combine(day, time(11, 30), TZ)),
            (datetime.combine(day, time(13, 0), TZ), datetime.combine(day, time(15, 0), TZ))]


def is_trading_time(value: datetime) -> bool:
    local = value.astimezone(TZ)
    return any(start <= local <= end for start, end in session_for(local.date()))
