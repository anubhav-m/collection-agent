"""Request and response models for the chat and conversation routes."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.agent.state import ConversationState, ConversationStatus
from app.db.records import ConversationEvent, EventKind
from app.policy.models import EscalationReason


class ChatRequest(BaseModel):
    # extra="forbid": a client cannot send "verified" or "status" and have it ignored silently.
    model_config = ConfigDict(extra="forbid")

    conversation_id: str | None = Field(default=None, max_length=64)
    lender_id: str | None = Field(default=None, max_length=32)
    message: str = Field(min_length=1, max_length=2000)


class EventView(BaseModel):
    kind: EventKind
    text: str | None = None
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    tool_name: str | None = None
    accepted: bool | None = None
    reason: str | None = None
    result: dict[str, Any] | None = None
    created_at: datetime

    @classmethod
    def from_event(cls, event: ConversationEvent) -> "EventView":
        # Thought signatures are opaque provider bytes; they stay server-side.
        calls = [{"name": c.get("name"), "args": c.get("args", {})} for c in event.tool_calls]
        return cls.model_validate(event.model_dump(exclude={"tool_calls"}) | {"tool_calls": calls})


class ConversationView(BaseModel):
    conversation_id: str
    lender_id: str
    status: ConversationStatus
    verified: bool
    failed_verifications: int
    escalation_reason: EscalationReason | None
    created_at: datetime
    events: list[EventView]

    @classmethod
    def build(cls, state: ConversationState, events: list[ConversationEvent]) -> "ConversationView":
        return cls(
            conversation_id=state.conversation_id,
            lender_id=state.lender_id,
            status=state.status,
            verified=state.is_verified,
            failed_verifications=state.failed_verifications,
            escalation_reason=state.escalation_reason,
            created_at=state.created_at,
            events=[EventView.from_event(e) for e in events],
        )
