"""Server-side conversation state. Only server code changes it, never the client or model."""

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field

from app.policy.models import EscalationReason

MAX_VERIFICATION_ATTEMPTS = 3


class ConversationStatus(StrEnum):
    ACTIVE = "active"
    ESCALATED = "escalated"


def new_conversation_id() -> str:
    return f"CONV-{uuid4().hex}"


class ConversationState(BaseModel):
    conversation_id: str = Field(default_factory=new_conversation_id)
    lender_id: str
    status: ConversationStatus = ConversationStatus.ACTIVE
    verified_borrower_id: str | None = None
    failed_verifications: int = 0
    escalation_reason: EscalationReason | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_verified(self) -> bool:
        return self.verified_borrower_id is not None

    @property
    def is_escalated(self) -> bool:
        return self.status is ConversationStatus.ESCALATED

    @property
    def verification_attempts_left(self) -> int:
        return max(0, MAX_VERIFICATION_ATTEMPTS - self.failed_verifications)
