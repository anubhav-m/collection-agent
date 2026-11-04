"""Due dates for an accepted plan."""

import calendar
from datetime import date, timedelta

from app.policy.models import Frequency, PlanTerms


def add_months(start: date, months: int) -> date:
    month_index = start.month - 1 + months
    year, month = start.year + month_index // 12, month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def due_dates(terms: PlanTerms) -> list[date]:
    count = len(terms.payments)
    if terms.frequency is Frequency.MONTHLY:
        return [add_months(terms.start_date, i) for i in range(count)]
    step = 7 if terms.frequency is Frequency.WEEKLY else 14
    return [terms.start_date + timedelta(days=step * i) for i in range(count)]
