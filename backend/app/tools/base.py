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


@dataclass
class ToolContext:
    state: ConversationState
    policy: LenderPolicy
    repos: Repositories
    today: date


class ToolOutcome(BaseModel):
    ok: bool
    data: dict[str, Any] = {}
    error: str | None = None
    message: str | None = None
    # True when this call escalated the conversation, so the turn ends in a handoff.
    escalated: bool = False

    def for_model(self) -> dict[str, Any]:
        if self.ok:
            return {"ok": True} | self.data
        return {"ok": False, "error": self.error, "message": self.message} | self.data


def accepted(**data: Any) -> ToolOutcome:
    return ToolOutcome(ok=True, data=data)


def rejected(error: str, message: str, **data: Any) -> ToolOutcome:
    return ToolOutcome(ok=False, error=error, message=message, data=data)


def schema_for(model: type[BaseModel]) -> dict[str, Any]:
    """JSON schema with $refs inlined and titles dropped, to keep the prompt small."""
    schema = model.model_json_schema()
    defs = schema.pop("$defs", {})

    def clean(node: Any) -> Any:
        if isinstance(node, list):
            return [clean(item) for item in node]
        if not isinstance(node, dict):
            return node
        if "$ref" in node:
            return clean(defs[node["$ref"].rsplit("/", 1)[-1]])
        return {k: clean(v) for k, v in node.items() if k != "title"}

    return clean(schema)


@dataclass(frozen=True)
class Tool:
    spec: ToolSpec
    args_model: type[BaseModel]
    run: Callable[[ToolContext, Any], Awaitable[ToolOutcome]]
    requires_verification: bool
    allowed_after_escalation: bool
