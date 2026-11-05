"""Render a finished run as Markdown."""

from app.evaluation.results import RunFile


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _summary(run: RunFile) -> list[str]:
    m, meta = run.metrics or {}, run.meta
    usage, turn, call = m["llm_usage"], m["turn_latency_ms"], m["llm_call_latency_ms"]
    return [
        f"# Evaluation: {meta.run_name}",
        "",
        f"- Model: `{meta.model}`; commit `{meta.git_commit[:10]}`"
        f"{' (dirty)' if meta.git_dirty else ''}; official run: {meta.official}",
        f"- Scenarios: {m['scenario_count']} (set `{meta.scenario_set_hash}`); "
        f"evaluation date {meta.eval_today}",
        f"- Started {meta.started_at:%Y-%m-%d %H:%M} UTC, finished "
        f"{meta.finished_at:%Y-%m-%d %H:%M} UTC"
        if meta.finished_at
        else "- Not finished",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Task success rate | {_pct(m['task_success_rate'])} "
        f"({m['passed']}/{m['scenario_count']}) |",
        f"| Escalation accuracy | {_pct(m['escalation_accuracy'])} |",
        f"| Missed / false escalations | {m['missed_escalations']} / {m['false_escalations']} |",
        f"| Unauthorized actions | {m['unauthorized_actions']} |",
        f"| Blocked tool attempts | {m['blocked_attempts'] or 'none'} |",
        f"| Turn latency avg / p95 | {turn['avg']} / {turn['p95']} ms ({turn['count']} turns) |",
        f"| LLM call latency avg / p95 | {call['avg']} / {call['p95']} ms |",
        f"| LLM calls | {usage['calls']} |",
        f"| Tokens prompt / output / thinking / total | {usage['prompt_tokens']} / "
        f"{usage['output_tokens']} / {usage['thinking_tokens']} / {usage['total_tokens']} |",
    ]


def render_markdown(run: RunFile) -> str:
    lines = _summary(run)
    lines += ["", "## By category", "", "| Category | Passed |", "|---|---|"]
    for name, row in (run.metrics or {})["by_category"].items():
        lines.append(f"| {name} | {row['passed']}/{row['total']} |")
    lines += ["", "## Scenarios", "", "| Scenario | Result | Reasons |", "|---|---|---|"]
    for r in run.results:
        label = f"{r.id}{' (hard)' if r.hard else ''}"
        reasons = "<br>".join(f.replace("|", r"\|") for f in r.failures) or "all checks passed"
        lines.append(f"| {label} | {'PASS' if r.passed else 'FAIL'} | {reasons} |")
    return "\n".join(lines) + "\n"
