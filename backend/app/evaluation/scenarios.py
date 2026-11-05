"""Scenario files: scripted borrower turns plus what the code checks expect."""

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from app.policy.models import EscalationReason, Frequency


class PlanExpect(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str
    installments: int
    frequency: Frequency | None = None


class Expectation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    escalated: bool
    escalation_reason: EscalationReason | None = None
    verified: bool | None = None
    failed_verifications: int | None = None
    plan: PlanExpect | None = None
    no_plan: bool = False
    tools_accepted: list[str] = []
    tools_requested: list[str] = []
    tools_not_accepted: list[str] = []
    reply_includes_any: list[str] = []  # checked on the final reply
    replies_exclude: list[str] = []  # checked on every reply
    admits_unknown: bool = False
    sources_include: list[str] = []
    sources_exclude: list[str] = []


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    category: str
    lender_id: str
    description: str
    hard: bool = False
    turns: list[str] = Field(min_length=1)
    expect: Expectation


def load_scenarios(directory: Path) -> list[Scenario]:
    """Every *.json file holds a list of scenarios. Fails loudly on a bad file or a duplicate."""
    scenarios: list[Scenario] = []
    for path in sorted(directory.glob("*.json")):
        items = json.loads(path.read_text(encoding="utf-8"))
        scenarios.extend(Scenario.model_validate(item) for item in items)
    ids = [s.id for s in scenarios]
    if dupes := sorted({i for i in ids if ids.count(i) > 1}):
        raise ValueError(f"duplicate scenario ids: {dupes}")
    if not scenarios:
        raise ValueError(f"no scenarios found in {directory}")
    return scenarios


def scenario_set_hash(scenarios: list[Scenario]) -> str:
    """Changes whenever any scenario changes, so only identical sets get compared."""
    raw = json.dumps([s.model_dump(mode="json") for s in scenarios], sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
