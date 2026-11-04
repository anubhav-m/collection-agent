from datetime import timedelta
from decimal import Decimal

import pytest

from app.policy.models import Frequency, PlanTerms
from app.policy.rules import payment_options, plan_violations, split_evenly, to_money
from tests.fakes.context import POLICIES, TODAY

LND1 = POLICIES.get("LND-001")  # counts 1/3/6/12, min 25.00, first payment within 30 days
BALANCE = to_money("850.50")


def terms(payments, frequency=Frequency.MONTHLY, start=TODAY) -> PlanTerms:
    return PlanTerms(frequency=frequency, payments=[Decimal(p) for p in payments], start_date=start)


def test_split_evenly_adds_up_and_puts_remainder_last():
    payments = split_evenly(to_money("100.00"), 3)
    assert payments == [Decimal("33.33"), Decimal("33.33"), Decimal("33.34")]


def test_options_respect_counts_and_minimum_payment():
    options = payment_options(LND1, to_money("60.00"))
    # 6 or 12 payments of 60.00 would fall below the 25.00 minimum.
    assert [o.installments for o in options] == [1]
    assert all(sum(o.payments) == BALANCE for o in payment_options(LND1, BALANCE))


def test_valid_plan_has_no_violations():
    assert plan_violations(LND1, BALANCE, terms(["283.50"] * 3), TODAY) == []


def test_single_full_payment_is_allowed_below_minimum():
    assert plan_violations(LND1, to_money("10.00"), terms(["10.00"]), TODAY) == []


@pytest.mark.parametrize(
    ("plan", "expected"),
    [
        (terms(["425.25"] * 2), "installments must be one of"),
        (terms(["283.50", "283.50", "283.49"]), "add up to the balance"),
        (terms(["283.505", "283.50", "283.495"]), "whole cents"),
        (terms(["400.00", "430.50", "20.00"]), "at least 25.00"),
        (terms(["283.50"] * 3, start=TODAY - timedelta(days=1)), "start date"),
        (terms(["283.50"] * 3, start=TODAY + timedelta(days=31)), "start date"),
    ],
)
def test_rule_breaking_plans_are_rejected(plan, expected):
    problems = plan_violations(LND1, BALANCE, plan, TODAY)
    assert any(expected in p for p in problems), problems


def test_frequency_must_be_allowed_by_lender():
    lnd2 = POLICIES.get("LND-002")  # monthly only
    plan = terms(["1510.00", "1510.00"], frequency=Frequency.WEEKLY)
    assert any("frequency" in p for p in plan_violations(lnd2, to_money("3020.00"), plan, TODAY))
