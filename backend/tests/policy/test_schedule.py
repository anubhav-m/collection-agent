from datetime import date
from decimal import Decimal

from app.policy.models import Frequency, PlanTerms
from app.policy.schedule import due_dates


def plan(frequency: Frequency, start: date) -> PlanTerms:
    return PlanTerms(frequency=frequency, payments=[Decimal("1")] * 3, start_date=start)


def test_monthly_dates_clamp_to_month_end():
    dates = due_dates(plan(Frequency.MONTHLY, date(2026, 12, 31)))
    assert dates == [date(2026, 12, 31), date(2027, 1, 31), date(2027, 2, 28)]


def test_weekly_and_biweekly_steps():
    start = date(2026, 11, 10)
    assert due_dates(plan(Frequency.WEEKLY, start))[2] == date(2026, 11, 24)
    assert due_dates(plan(Frequency.BIWEEKLY, start))[2] == date(2026, 12, 8)
