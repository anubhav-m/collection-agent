"""Write fake nightly run folders the way the run scripts and report_cli do."""

import json
from pathlib import Path


def run_doc(run_id: str, status: str = "success", failed_step: str | None = None) -> dict:
    step = {"name": "extract", "status": status, "exit_code": 0 if status == "success" else 1,
            "seconds": 1.5}  # fmt: skip
    return {
        "run_id": run_id, "as_of": run_id[:10], "status": status,
        "started_at": "2026-11-05T10:00:00+05:30", "finished_at": "2026-11-05T10:01:00+05:30",
        "failed_step": failed_step, "exit_code": step["exit_code"], "steps": [step],
    }  # fmt: skip


def report_doc(source: str, rows: int = 1) -> dict:
    return {
        "source": source, "note": "n", "as_of": "2026-11-05", "params": {},
        "generated_at": "2026-11-05T04:31:00+00:00", "row_counts": {"followups": rows},
        "reports": {"followups": [{"promise_id": f"P{i}"} for i in range(rows)]},
    }  # fmt: skip


def write_run(root: Path, run_id: str, status: str = "success", **reports: int) -> Path:
    folder = root / run_id
    folder.mkdir(parents=True)
    failed = None if status == "success" else "extract"
    run = run_doc(run_id, status, failed)
    (folder / "run.json").write_text(json.dumps(run), encoding="utf-8")
    (root / "last_run.json").write_text(json.dumps(run), encoding="utf-8")
    for source, rows in reports.items():
        (folder / f"{source}.json").write_text(json.dumps(report_doc(source, rows)), "utf-8")
    return folder
