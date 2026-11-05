"""Render a benchmark report as Markdown."""

from app.extraction.metrics import ENTITY_TYPES
from app.extraction.report import BenchmarkReport, ExtractorResult


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _scores_table(results: list[ExtractorResult]) -> list[str]:
    rows = [
        "| Extractor | Entity | Precision | Recall | F1 | TP / FP / FN |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        for name in ENTITY_TYPES:
            s = r.metrics["entities"][name]
            counts = f"{s['tp']} / {s['fp']} / {s['fn']}"
            rows.append(
                f"| {r.extractor} | {name} | {_pct(s['precision'])} | {_pct(s['recall'])} "
                f"| {_pct(s['f1'])} | {counts} |"
            )
    return rows


def _cost_table(results: list[ExtractorResult]) -> list[str]:
    rows = [
        "| Extractor | Exact match | Errors | Latency avg / p95 (ms) | Tokens prompt / output |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        m = r.metrics
        lat, tok = m["latency_ms"], m["tokens"]
        rows.append(
            f"| {r.extractor} | {_pct(m['exact_match_rate'])} | {m['errors']} "
            f"| {lat['avg']:,} / {lat['p95']:,} | {tok['prompt']:,} / {tok['output']:,} |"
        )
    return rows


def _misses(r: ExtractorResult) -> list[str]:
    rows = [f"### {r.extractor}: transcripts not fully correct", ""]
    for o, lb in zip(r.outcomes, r.labels, strict=True):
        e = o.entities
        got = (e.promise_made, e.amount, e.date) if e else ("error", o.error, None)
        want = (lb.promise_made, lb.amount, lb.date)
        if e is None or (e.promise_made, e.amount, e.date) != want:
            rows.append(f"- `{lb.id}` ({lb.case}): got {got}, expected {want}")
    return rows if len(rows) > 2 else [*rows, "- none"]


def render_markdown(report: BenchmarkReport) -> str:
    m = report.meta
    head = [
        f"# Extraction benchmark: {m.run_name}",
        "",
        f"- Split: **{m.split}** ({len(m.transcript_ids)} transcripts), official: {m.official}",
        f"- Model: `{m.model}`, commit `{m.git_commit[:10]}`",
        f"- Pacing: {m.requests_per_minute} requests/min, {m.gap_seconds} s between LLM calls",
        f"- Started {m.started_at:%Y-%m-%d %H:%M} UTC",
        "- An amount or date counts only if exactly right; a wrong value is one FP and one FN.",
        "",
    ]
    body = [*_scores_table(report.results), "", *_cost_table(report.results), ""]
    for r in report.results:
        body += [*_misses(r), ""]
    return "\n".join(head + body)
