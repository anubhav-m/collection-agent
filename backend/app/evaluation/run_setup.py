"""Pick the scenarios for a run and describe the setup it runs under."""

from datetime import UTC, datetime

from app.evaluation.environment import EVAL_TODAY, SCENARIOS_DIR
from app.evaluation.git_info import current_commit, evaluated_code_dirty
from app.evaluation.results import RunMeta
from app.evaluation.scenarios import Scenario, load_scenarios, scenario_set_hash


def prepare(name: str, only: str | None, model: str) -> tuple[list[Scenario], RunMeta]:
    """A run with --only is a debug run; only full runs are official and comparable."""
    scenarios = load_scenarios(SCENARIOS_DIR)
    if only:
        wanted = set(only.split(","))
        if unknown := wanted - {s.id for s in scenarios}:
            raise ValueError(f"unknown scenario ids: {sorted(unknown)}")
        scenarios = [s for s in scenarios if s.id in wanted]
    meta = RunMeta(
        run_name=name,
        official=not only,
        model=model,
        git_commit=current_commit(),
        git_dirty=evaluated_code_dirty(),
        scenario_set_hash=scenario_set_hash(scenarios),
        scenario_count=len(scenarios),
        eval_today=EVAL_TODAY,
        started_at=datetime.now(UTC),
    )
    return scenarios, meta
