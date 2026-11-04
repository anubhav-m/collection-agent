"""Stored shapes for conversation events, payment plans and escalations."""

from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.policy.models import EscalationReason, Frequency


def utc_now() -> datetime:
    return datetime.now(UTC)


class EventKind(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ESCALATION = "escalation"


class ConversationEvent(BaseModel):
    conversation_id: str
    kind: EventKind
    text: str | None = None
    # tool_call events hold every call from one model reply, signatures included.
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    tool_name: str | None = None
    call_id: str | None = None
    accepted: bool | None = None
    reason: str | None = None
    result: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=utc_now)


class PaymentPlan(BaseModel):
    plan_id: str
    idempotency_key: str
    conversation_id: str
    borrower_id: str
    account_id: str
    lender_id: str
    frequency: Frequency
    payments: list[Decimal]
    start_date: date
    total: Decimal
    status: str = "active"
    is_fictional: bool = True
    created_at: datetime = Field(default_factory=utc_now)


class Escalation(BaseModel):
    conversation_id: str
    lender_id: str
    borrower_id: str | None
    reason: EscalationReason
    source: str  # "rule", "model" or "verification_limit"
    summary: str = ""
    created_at: datetime = Field(default_factory=utc_now)
