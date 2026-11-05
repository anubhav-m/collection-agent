"""Compare two complete official runs on the same model and scenario set."""

from app.evaluation.results import RunFile

METRICS = [
    "task_success_rate",
    "escalation_accuracy",
    "missed_escalations",
    "false_escalations",
    "unauthorized_actions",
]


def comparable(before: RunFile, after: RunFile) -> str | None:
    """Return why two runs can't be compared, or None if they can."""
    for run in (before, after):
        if not run.meta.official or run.metrics is None:
            return f"{run.meta.run_name} is not a complete official run"
    if before.meta.model != after.meta.model:
        return "the runs used different models"
    if before.meta.scenario_set_hash != after.meta.scenario_set_hash:
        return "the runs used different scenario sets"
    return None


def compare(before: RunFile, after: RunFile) -> dict:
    b, a = before.metrics or {}, after.metrics or {}
    was = {r.id: r.passed for r in before.results}
    now = {r.id: r.passed for r in after.results}
    return {
        "before": before.meta.model_dump(mode="json"),
        "after": after.meta.model_dump(mode="json"),
        "metrics": {k: {"before": b[k], "after": a[k]} for k in METRICS}
        | {
            "turn_latency_p95_ms": {
                "before": b["turn_latency_ms"]["p95"],
                "after": a["turn_latency_ms"]["p95"],
            },
            "llm_total_tokens": {
                "before": b["llm_usage"]["total_tokens"],
                "after": a["llm_usage"]["total_tokens"],
            },
        },
        "fixed": sorted(i for i in now if now[i] and not was[i]),
        "regressed": sorted(i for i in now if was[i] and not now[i]),
        "still_failing": sorted(i for i in now if not now[i] and not was[i]),
    }


def render(diff: dict) -> str:
    lines = [
        "# Evaluation comparison",
        "",
        f"Before: `{diff['before']['run_name']}` at `{diff['before']['git_commit'][:10]}`. "
        f"After: `{diff['after']['run_name']}` at `{diff['after']['git_commit'][:10]}`. "
        f"Model `{diff['after']['model']}`, scenario set `{diff['after']['scenario_set_hash']}`.",
        "",
        "| Metric | Before | After |",
        "|---|---|---|",
    ]
    lines += [f"| {k} | {v['before']} | {v['after']} |" for k, v in diff["metrics"].items()]
    for key in ("fixed", "regressed", "still_failing"):
        lines += ["", f"**{key.replace('_', ' ').capitalize()}:** {', '.join(diff[key]) or 'none'}"]
    return "\n".join(lines) + "\n"
