"""In-memory conversation and event repositories, matching the Mongo interface."""

from app.agent.state import ConversationState, ConversationStatus
from app.db.records import ConversationEvent
from app.policy.models import EscalationReason


class MemoryConversations:
    def __init__(self) -> None:
        self.items: dict[str, ConversationState] = {}

    async def create(self, state: ConversationState) -> None:
        self.items[state.conversation_id] = state.model_copy(deep=True)

    async def get(self, conversation_id: str) -> ConversationState | None:
        state = self.items.get(conversation_id)
        return state.model_copy(deep=True) if state else None

    async def mark_verified(self, conversation_id: str, borrower_id: str) -> None:
        self.items[conversation_id].verified_borrower_id = borrower_id

    async def add_failed_verification(self, conversation_id: str) -> int:
        self.items[conversation_id].failed_verifications += 1
        return self.items[conversation_id].failed_verifications

    async def escalate(self, conversation_id: str, reason: EscalationReason) -> bool:
        state = self.items[conversation_id]
        if state.is_escalated:
            return False
        state.status, state.escalation_reason = ConversationStatus.ESCALATED, reason
        return True


class MemoryEvents:
    def __init__(self) -> None:
        self.items: list[ConversationEvent] = []

    async def append(self, event: ConversationEvent) -> None:
        self.items.append(event)

    async def list(self, conversation_id: str) -> list[ConversationEvent]:
        return [e for e in self.items if e.conversation_id == conversation_id]
