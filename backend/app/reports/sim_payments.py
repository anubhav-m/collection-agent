"""Decide how a simulated promise was paid. Payments after the anchor date have not
happened yet, so they are never generated."""

import random
from datetime import date, timedelta

from app.reports.rows_money import PaymentRow, PromiseRow
from app.reports.sim_profiles import LenderProfile, SimulationConfig


def _pay(promise: PromiseRow, n: int, cents: int, day: date) -> PaymentRow:
    return PaymentRow(
        f"SIM-PAY-{promise.promise_id[8:]}-{n}", promise.promise_id, promise.lender_id,
        promise.borrower_id, cents, day.isoformat(), "simulated",
    )  # fmt: skip


def _day_between(rng: random.Random, start: date, end: date) -> date:
    return start + timedelta(days=rng.randint(0, max(0, (end - start).days)))


def simulate_payments(
    rng: random.Random, promise: PromiseRow, profile: LenderProfile,
    cfg: SimulationConfig, anchor: date,
) -> list[PaymentRow]:  # fmt: skip
    if promise.amount_cents is None or promise.due_date is None:
        return []
    start, due = date.fromisoformat(promise.promised_on), date.fromisoformat(promise.due_date)
    amount, roll = promise.amount_cents, rng.random()
    if roll < profile.keep_rate:
        if rng.random() < 0.25:  # paid in two parts, both on time
            half = amount // 2
            plan = [(half, _day_between(rng, start, due)), (amount - half, due)]
        else:
            plan = [(amount, _day_between(rng, start, due))]
    elif roll < profile.keep_rate + cfg.partial_rate:
        plan = [(int(amount * rng.uniform(0.3, 0.7)), _day_between(rng, start, due))]
    elif roll < profile.keep_rate + cfg.partial_rate + cfg.late_rate:
        plan = [(amount, due + timedelta(days=rng.randint(1, 10)))]
    else:
        plan = []
    paid = [(cents, day) for cents, day in plan if cents > 0 and day <= anchor]
    return [_pay(promise, n, cents, day) for n, (cents, day) in enumerate(paid, start=1)]
