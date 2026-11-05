"""Calendar arithmetic for relative dates. The rules match data/extraction/README.md."""

import calendar
from datetime import date, timedelta


def next_weekday(ref: date, weekday: int) -> date:
    """The next such weekday strictly after ref (Monday is 0)."""
    return ref + timedelta(days=(weekday - ref.weekday() - 1) % 7 + 1)


def weekday_next_week(ref: date, weekday: int) -> date:
    """That weekday in the calendar week after ref's week (weeks start on Monday)."""
    next_monday = ref + timedelta(days=7 - ref.weekday())
    return next_monday + timedelta(days=weekday)


def next_day_of_month(ref: date, day: int) -> date | None:
    """The next date on or after ref whose day of month is `day`."""
    year, month = ref.year, ref.month
    for _ in range(3):
        if day <= calendar.monthrange(year, month)[1]:
            candidate = date(year, month, day)
            if candidate >= ref:
                return candidate
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return None


def month_day(ref: date, month: int, day: int) -> date | None:
    """A month and day with no year: this year, or next year if already past."""
    for year in (ref.year, ref.year + 1):
        if day <= calendar.monthrange(year, month)[1] and date(year, month, day) >= ref:
            return date(year, month, day)
    return None


def end_of_month(ref: date) -> date:
    return date(ref.year, ref.month, calendar.monthrange(ref.year, ref.month)[1])
