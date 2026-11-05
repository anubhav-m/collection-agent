"""Read the committed evaluation and extraction reports for the results view.
Only reads saved files, so every number shown comes from a report in the repo."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

EVALUATION_RUNS = ("baseline", "latest")
EXTRACTION_SPLIT = "test"


class ResultsUnreadableError(Exception):
    """A report file exists but cannot be parsed."""


class EvaluationRun(BaseModel):
    run_name: str
    model: str
    git_commit: str
    finished_at: str
    scenario_count: int
    passed: int
    task_success_rate: float
    escalation_accuracy: float
    missed_escalations: int
    false_escalations: int
    unauthorized_actions: int
    llm_calls: int
    by_category: dict[str, dict[str, int]]
    report_path: str


class EntityScore(BaseModel):
    precision: float
    recall: float
    f1: float


class ExtractionRun(BaseModel):
    extractor: str
    split: str
    model: str | None  # None for the regex extractor, which uses no model
    transcripts: int
    exact_match_rate: float
    entities: dict[str, EntityScore]
    report_path: str


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ResultsUnreadableError(f"{path.name}: {type(exc).__name__}") from exc


def repo_path(path: Path, reports_dir: Path) -> str:
    """The report's path as linked from the repo root, for example reports/evaluation/x.md."""
    return f"reports/{path.relative_to(reports_dir).as_posix()}"
