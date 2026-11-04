"""Rules engine: which payment plans a lender allows for a given balance."""

from datetime import date, timedelta
from decimal import ROUND_DOWN, Decimal

from app.policy.models import LenderPolicy, PlanOption, PlanTerms

CENT = Decimal("0.01")


def to_money(value: float | str | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(CENT)


def split_evenly(balance: Decimal, installments: int) -> list[Decimal]:
    """Equal payments rounded down to the cent; the last one absorbs the remainder."""
    base = (balance / installments).quantize(CENT, rounding=ROUND_DOWN)
    return [base] * (installments - 1) + [balance - base * (installments - 1)]


def payment_options(policy: LenderPolicy, balance: Decimal) -> list[PlanOption]:
    options = []
    for count in policy.allowed_installment_counts:
        payments = split_evenly(balance, count)
        if min(payments) < policy.min_payment and count > 1:
            continue
        options.append(PlanOption(installments=count, payments=payments))
    return options


def plan_violations(
    policy: LenderPolicy, balance: Decimal, terms: PlanTerms, today: date
) -> list[str]:
    """Return every rule the plan breaks. An empty list means the plan is allowed."""
    problems = []
    payments = terms.payments
    if len(payments) not in policy.allowed_installment_counts:
        problems.append(f"installments must be one of {policy.allowed_installment_counts}")
    if any(p != p.quantize(CENT) for p in payments):
        problems.append("payments must be whole cents")
    # A single payment of the full balance is always allowed, even below the minimum.
    if len(payments) > 1 and any(p < policy.min_payment for p in payments):
        problems.append(f"each payment must be at least {policy.min_payment}")
    if sum(payments, Decimal(0)) != balance:
        problems.append(f"payments must add up to the balance of {balance}")
    if terms.frequency not in policy.allowed_frequencies:
        allowed = [f.value for f in policy.allowed_frequencies]
        problems.append(f"frequency must be one of {allowed}")
    latest = today + timedelta(days=policy.max_days_to_first_payment)
    if not today <= terms.start_date <= latest:
        problems.append(f"start date must be between {today} and {latest}")
    return problems
