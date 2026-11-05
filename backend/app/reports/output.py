"""Write one source's report results as JSON, plus a short Markdown summary of a run."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.reports.queries import ReportParams

NOTES = {
    "project": "Real project data from MongoDB and the extraction results.",
    "simulated": "SIMULATED history from a seeded generator. Not project results.",
}


def report_document(params: ReportParams, reports: dict[str, list[dict]]) -> dict[str, Any]:
    return {
        "source": params.source,
        "note": NOTES[params.source],
        "as_of": params.as_of.isoformat(),
        "params": params.bind(),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "row_counts": {name: len(rows) for name, rows in reports.items()},
        "reports": reports,
    }


def write_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2), encoding="utf-8")


def summary_markdown(documents: list[dict[str, Any]]) -> str:
    lines = ["# Nightly reports", ""]
    for doc in documents:
        lines += [f"## {doc['source']} (as of {doc['as_of']})", "", doc["note"], ""]
        lines += [f"- {name}: {count} rows" for name, count in doc["row_counts"].items()]
        lines += ["", "| Lender | Promises due | Kept | Kept rate |", "|---|---|---|---|"]
        lines += [
            f"| {r['lender_name']} | {r['promises_due']} | {r['promises_kept']} "
            f"| {r['kept_rate_pct']}% |"
            for r in doc["reports"]["kept_rate_lender"]
        ]
        followups = doc["reports"]["followups"]
        overdue = sum(1 for r in followups if r["followup_status"] == "overdue")
        lines += ["", f"Follow-ups: {len(followups)} ({overdue} overdue).", ""]
    return "\n".join(lines)
