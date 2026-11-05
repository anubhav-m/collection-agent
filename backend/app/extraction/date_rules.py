"""Date patterns and how each resolves against the reference date (see data/extraction/README.md).

Text must already have number and ordinal words turned into digits.
"""

import re
from collections.abc import Callable
from datetime import date, timedelta

from app.extraction import date_math as dm

MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

# Higher priority wins in a turn: an exact date beats "Friday" in "Friday, November 13".
EXACT, DAY_OF_MONTH, RELATIVE = 3, 2, 1
Resolver = Callable[[re.Match[str], date], date | None]


def _month(m: re.Match[str], ref: date) -> date | None:
    return dm.month_day(ref, MONTHS.index(m.group(1)[:3].lower()) + 1, int(m.group(2)))


def _slash(m: re.Match[str], ref: date) -> date | None:
    month, day = int(m.group(1)), int(m.group(2))
    return dm.month_day(ref, month, day) if 1 <= month <= 12 and 1 <= day <= 31 else None


def _day_of_month(m: re.Match[str], ref: date) -> date | None:
    return dm.next_day_of_month(ref, int(m.group(1)))


def _weekday(m: re.Match[str], ref: date) -> date:
    day = WEEKDAYS.index(m.group(2).lower())
    if (m.group(1) or "").lower() == "next":
        return dm.weekday_next_week(ref, day)
    return dm.next_weekday(ref, day)


def _offset(m: re.Match[str], ref: date) -> date:
    unit = 7 if m.group(2).lower().startswith("week") else 1
    count = 1 if m.group(1) in (None, "a") else int(m.group(1))
    return ref + timedelta(days=count * unit)


def _compile(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, re.IGNORECASE)


_MONTH_RE = rf"\b((?:{'|'.join(MONTHS)})[a-z]*)\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?\b"
_WEEKDAY_RE = rf"\b(?:(this|next)\s+)?({'|'.join(WEEKDAYS)})\b"
RULES: list[tuple[int, re.Pattern[str], Resolver]] = [
    (EXACT, _compile(_MONTH_RE), _month),
    (EXACT, _compile(r"(?<![\d/])(\d{1,2})/(\d{1,2})\b(?!/)"), _slash),
    (DAY_OF_MONTH, _compile(r"\bthe\s+(\d{1,2})(?:st|nd|rd|th)\b"), _day_of_month),
    (RELATIVE, _compile(r"\b(?:today|tonight)\b"), lambda m, ref: ref),
    (RELATIVE, _compile(r"\btomorrow\b"), lambda m, ref: ref + timedelta(days=1)),
    (RELATIVE, _compile(_WEEKDAY_RE), _weekday),
    (RELATIVE, _compile(r"\bin\s+(\d+|a)?\s*(days?|weeks?)\b"), _offset),
    (RELATIVE, _compile(r"\b(\d+|a)?\s*(days?|weeks?)\s+from\s+(?:today|now)\b"), _offset),
    (RELATIVE, _compile(r"\bend\s+of\s+(?:the\s+)?month\b"), lambda m, ref: dm.end_of_month(ref)),
]
