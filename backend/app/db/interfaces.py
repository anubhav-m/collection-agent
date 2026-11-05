"""Small repository interfaces. Mongo implements them; tests use in-memory fakes."""

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from app.agent.state import ConversationState
from app.db.models import Account, Borrower
from app.db.records import ConversationEvent, Escalation, PaymentPlan
from app.policy.models import EscalationReason


class ConversationRepo(Protocol):
    async def create(self, state: ConversationState) -> None: ...
    async def get(self, conversation_id: str) -> ConversationState | None: ...
    async def mark_verified(self, conversation_id: str, borrower_id: str) -> None: ...
    async def add_failed_verification(self, conversation_id: str) -> int: ...
    async def escalate(self, conversation_id: str, reason: EscalationReason) -> bool: ...


class EventRepo(Protocol):
    async def append(self, event: ConversationEvent) -> None: ...
    async def list(self, conversation_id: str) -> list[ConversationEvent]: ...


class BorrowerRepo(Protocol):
    async def find_by_identity(
        self, lender_id: str, date_of_birth: date, zip_code: str
    ) -> list[Borrower]: ...
    async def get_account(self, account_id: str) -> Account | None: ...
    async def list_accounts(self, borrower_id: str) -> list[Account]: ...


class PlanRepo(Protocol):
    async def find_active(self, account_id: str) -> PaymentPlan | None: ...
    async def insert_once(self, plan: PaymentPlan) -> tuple[PaymentPlan, bool]:
        """Save the plan unless an active one exists; return (stored plan, created)."""
        ...

    async def list_by_conversation(self, conversation_id: str) -> list[PaymentPlan]: ...


class EscalationRepo(Protocol):
    async def create_once(self, escalation: Escalation) -> bool: ...


@dataclass(frozen=True)
class Repositories:
    conversations: ConversationRepo
    events: EventRepo
    borrowers: BorrowerRepo
    plans: PlanRepo
    escalations: EscalationRepo
