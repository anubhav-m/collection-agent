"""Shared tool types: the context a tool runs in and the outcome it returns."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import date
from typing import Any

from pydantic import BaseModel

from app.agent.state import ConversationState
from app.db.interfaces import Repositories
from app.llm.types import ToolSpec
from app.policy.models import LenderPolicy
from app.rag.retriever import PolicyRetriever
from app.rag.types import PolicySource


@dataclass
class ToolContext:
    state: ConversationState
    policy: LenderPolicy
    repos: Repositories
    today: date
    retriever: PolicyRetriever | None = None


class ToolOutcome(BaseModel):
    ok: bool
    data: dict[str, Any] = {}
    error: str | None = None
    message: str | None = None
    # True when this call escalated the conversation, so the turn ends in a handoff.
    escalated: bool = False
    # Documents this call retrieved; returned to the API client, not part of for_model().
    sources: list[PolicySource] = []

    def for_model(self) -> dict[str, Any]:
        if self.ok:
            return {"ok": True} | self.data
        return {"ok": False, "error": self.error, "message": self.message} | self.data


def accepted(**data: Any) -> ToolOutcome:
    return ToolOutcome(ok=True, data=data)


def rejected(error: str, message: str, **data: Any) -> ToolOutcome:
    return ToolOutcome(ok=False, error=error, message=message, data=data)


@dataclass(frozen=True)
class Tool:
    spec: ToolSpec
    args_model: type[BaseModel]
    run: Callable[[ToolContext, Any], Awaitable[ToolOutcome]]
    requires_verification: bool
    allowed_after_escalation: bool
