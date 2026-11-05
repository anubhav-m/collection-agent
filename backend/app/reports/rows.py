"""Row shapes for the reporting tables. Field order matches the column order in schema.sql."""

from dataclasses import dataclass
from typing import Literal

Source = Literal["project", "simulated"]


@dataclass(frozen=True, slots=True)
class LenderRow:
    lender_id: str
    name: str
    source: Source


@dataclass(frozen=True, slots=True)
class BorrowerRow:
    borrower_id: str
    lender_id: str
    source: Source


@dataclass(frozen=True, slots=True)
class ConversationRow:
    conversation_id: str
    lender_id: str
    borrower_id: str | None
    status: str
    started_on: str
    source: Source


@dataclass(frozen=True, slots=True)
class EscalationRow:
    conversation_id: str
    lender_id: str
    borrower_id: str | None
    reason: str
    trigger_kind: str
    escalated_on: str
    source: Source
