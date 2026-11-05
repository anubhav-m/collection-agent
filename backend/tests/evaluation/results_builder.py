"""Build scenario results and run files for metric, progress and comparison tests."""

from datetime import UTC, date, datetime

from app.evaluation.checks import score
from app.evaluation.metrics import compute_metrics
from app.evaluation.results import RunFile, RunMeta, ScenarioResult
from tests.evaluation.builders import scenario, trace


def result(sid: str, passed: bool, escalated: bool = False) -> ScenarioResult:
    s = scenario(escalated=False).model_copy(update={"id": sid})
    t = trace(escalated=escalated, reason="dispute" if escalated else None)
    r = ScenarioResult.build(s, t, score(s, t))
    return r.model_copy(update={"passed": passed})


def meta(name: str = "baseline", commit: str = "abc123", model: str = "m-1") -> RunMeta:
    return RunMeta(
        run_name=name,
        official=True,
        model=model,
        git_commit=commit,
        git_dirty=False,
        scenario_set_hash="h1",
        scenario_count=2,
        eval_today=date(2026, 11, 5),
        started_at=datetime(2026, 11, 5, tzinfo=UTC),
    )


def run_file(name: str, results: list[ScenarioResult], **kw) -> RunFile:
    return RunFile(meta=meta(name, **kw), results=results, metrics=compute_metrics(results))
