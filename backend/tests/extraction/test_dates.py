from datetime import date

import pytest

from app.extraction import date_math as dm
from app.extraction.date_rules import EXACT, RELATIVE
from app.extraction.dates import find_dates

WED = date(2026, 11, 4)  # a Wednesday


def _best(text: str, ref: date = WED) -> date | None:
    found = find_dates(text, ref)
    return max(found, key=lambda d: (d[0], d[1]))[2] if found else None


@pytest.mark.parametrize(
    ("text", "ref", "expected"),
    [
        ("today", WED, date(2026, 11, 4)),
        ("tonight after work", WED, date(2026, 11, 4)),
        ("tomorrow", WED, date(2026, 11, 5)),
        ("Friday", WED, date(2026, 11, 6)),
        ("this Friday", WED, date(2026, 11, 6)),
        ("next Friday", WED, date(2026, 11, 13)),
        ("next Friday", date(2026, 11, 24), date(2026, 12, 4)),
        ("next Monday", date(2026, 11, 9), date(2026, 11, 16)),
        ("Wednesday", WED, date(2026, 11, 11)),  # a weekday alone is strictly after today
        ("the 15th", WED, date(2026, 11, 15)),
        ("the 1st", date(2026, 11, 16), date(2026, 12, 1)),
        ("on 11/20", WED, date(2026, 11, 20)),
        ("Dec 3", WED, date(2026, 12, 3)),
        ("in 2 weeks", date(2026, 10, 28), date(2026, 11, 11)),
        ("a week from today", date(2026, 11, 20), date(2026, 11, 27)),
        ("end of the month", WED, date(2026, 11, 30)),
        ("Friday, November 13", date(2026, 11, 10), date(2026, 11, 13)),
        ("sometime next week", WED, None),
        ("born 03/14/1988", WED, None),
    ],
)
def test_resolved_dates(text, ref, expected):
    assert _best(text, ref) == expected


def test_exact_date_outranks_weekday_in_the_same_text():
    priorities = {p for p, _, _ in find_dates("Friday, November 13", WED)}
    assert priorities == {EXACT, RELATIVE}


def test_month_day_in_the_past_rolls_to_next_year():
    assert dm.month_day(date(2026, 12, 20), 1, 5) == date(2027, 1, 5)
    assert dm.month_day(WED, 2, 30) is None


def test_day_of_month_skips_months_that_are_too_short():
    assert dm.next_day_of_month(date(2026, 2, 10), 31) == date(2026, 3, 31)
