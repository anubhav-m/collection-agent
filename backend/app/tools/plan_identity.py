"""Idempotency key and model-facing view for payment plans."""

import hashlib
from typing import Any

from app.db.records import PaymentPlan
from app.policy.models import PlanTerms
from app.policy.rules import to_money
from app.policy.schedule import due_dates


def plan_key(conversation_id: str, account_id: str, terms: PlanTerms) -> str:
    """Same conversation, account and terms always give the same key."""
    amounts = ",".join(f"{to_money(p):.2f}" for p in terms.payments)
    raw = f"{conversation_id}|{account_id}|{terms.frequency}|{terms.start_date}|{amounts}"
    return hashlib.sha256(raw.encode()).hexdigest()


def plan_view(plan: PaymentPlan) -> dict[str, Any]:
    dates = due_dates(stored_terms(plan))
    return {
        "plan_id": plan.plan_id,
        "account_id": plan.account_id,
        "frequency": plan.frequency.value,
        "total": f"{plan.total:.2f}",
        "schedule": [
            {"due_date": d.isoformat(), "amount": f"{p:.2f}"}
            for d, p in zip(dates, plan.payments, strict=True)
        ],
    }


def stored_terms(plan: PaymentPlan) -> PlanTerms:
    return PlanTerms(frequency=plan.frequency, payments=plan.payments, start_date=plan.start_date)
