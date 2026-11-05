"""Stored shapes for one scenario's result and a whole run (also the progress file)."""

from datetime import date, datetime

from pydantic import BaseModel

from app.evaluation.check_result import CheckResult
from app.evaluation.checks import ScenarioScore
from app.evaluation.scenarios import Scenario
from app.evaluation.trace import ScenarioTrace


class ScenarioResult(BaseModel):
    id: str
    category: str
    hard: bool
    passed: bool
    failures: list[str]
    checks: list[CheckResult]
    expected_escalated: bool
    expected_reason: str | None
    escalation_correct: bool
    unauthorized_actions: int
    blocked_attempts: dict[str, int]
    trace: ScenarioTrace

    @classmethod
    def build(cls, scenario: Scenario, trace: ScenarioTrace, s: ScenarioScore) -> "ScenarioResult":
        reason = scenario.expect.escalation_reason
        return cls(
            id=scenario.id,
            category=scenario.category,
            hard=scenario.hard,
            passed=s.passed,
            failures=s.failures,
            checks=s.checks,
            expected_escalated=scenario.expect.escalated,
            expected_reason=reason.value if reason else None,
            escalation_correct=s.escalation_correct,
            unauthorized_actions=s.unauthorized_actions,
            blocked_attempts=s.blocked_attempts,
            trace=trace,
        )


class RunMeta(BaseModel):
    run_name: str
    official: bool
    model: str
    git_commit: str
    git_dirty: bool
    scenario_set_hash: str
    scenario_count: int
    eval_today: date
    started_at: datetime
    finished_at: datetime | None = None

    def same_setup(self, other: "RunMeta") -> bool:
        """A resumed run must match on model, commit, scenarios and evaluation date."""
        keys = ("model", "git_commit", "scenario_set_hash", "eval_today", "official")
        return all(getattr(self, k) == getattr(other, k) for k in keys)


class RunFile(BaseModel):
    meta: RunMeta
    results: list[ScenarioResult] = []
    metrics: dict | None = None
