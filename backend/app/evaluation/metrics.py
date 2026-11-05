"""Run-level metrics computed from the scenario results."""

import math
from statistics import mean

from app.evaluation.results import ScenarioResult


def p95(values: list[float]) -> float:
    """Nearest-rank 95th percentile."""
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]


def _latency(values: list[float]) -> dict[str, float]:
    return {"avg": round(mean(values), 1) if values else 0.0, "p95": round(p95(values), 1)}


def compute_metrics(results: list[ScenarioResult]) -> dict:
    n = len(results)
    traces = [r.trace for r in results]
    turn_ms = [t.latency_ms for tr in traces for t in tr.turns]
    call_ms = [ms for tr in traces for ms in tr.usage.call_latencies_ms]
    blocked: dict[str, int] = {}
    for r in results:
        for reason, count in r.blocked_attempts.items():
            blocked[reason] = blocked.get(reason, 0) + count
    by_category: dict[str, dict[str, int]] = {}
    for r in results:
        row = by_category.setdefault(r.category, {"passed": 0, "total": 0})
        row["total"] += 1
        row["passed"] += int(r.passed)
    usage_keys = ("calls", "prompt_tokens", "output_tokens", "thinking_tokens", "total_tokens")
    return {
        "scenario_count": n,
        "passed": sum(r.passed for r in results),
        "task_success_rate": round(sum(r.passed for r in results) / n, 3) if n else 0.0,
        "escalation_accuracy": round(sum(r.escalation_correct for r in results) / n, 3)
        if n
        else 0.0,
        "missed_escalations": sum(r.expected_escalated and not r.trace.escalated for r in results),
        "false_escalations": sum(r.trace.escalated and not r.expected_escalated for r in results),
        "unauthorized_actions": sum(r.unauthorized_actions for r in results),
        "blocked_attempts": dict(sorted(blocked.items())),
        "turn_latency_ms": _latency(turn_ms) | {"count": len(turn_ms)},
        "llm_call_latency_ms": _latency(call_ms) | {"count": len(call_ms)},
        "llm_usage": {k: sum(getattr(tr.usage, k) for tr in traces) for k in usage_keys},
        "by_category": dict(sorted(by_category.items())),
    }
