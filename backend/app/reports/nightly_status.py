"""Read nightly run results from reports/nightly/. The run scripts write run.json in each
dated run folder and copy it to last_run.json; report_cli writes <source>.json."""

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ValidationError

LAST_RUN = "last_run.json"


class NightlyStatusError(Exception):
    """A status or report file exists but cannot be read."""


class NightlyStep(BaseModel):
    name: str
    status: Literal["success", "failed"]
    exit_code: int
    seconds: float


class NightlyRun(BaseModel):
    run_id: str
    as_of: str
    status: Literal["success", "failed"]
    started_at: datetime
    finished_at: datetime
    failed_step: str | None = None
    exit_code: int
    steps: list[NightlyStep]


class ReportDocument(BaseModel):
    source: Literal["project", "simulated"]
    note: str
    as_of: str
    generated_at: datetime
    row_counts: dict[str, int]
    reports: dict[str, list[dict[str, Any]]]


def _read[M: BaseModel](path: Path, model: type[M]) -> M:
    try:
        return model.model_validate_json(path.read_bytes())
    except (OSError, ValidationError) as exc:
        raise NightlyStatusError(f"{path.name}: {type(exc).__name__}") from exc


def read_last_run(nightly_dir: Path) -> NightlyRun | None:
    path = nightly_dir / LAST_RUN
    return _read(path, NightlyRun) if path.exists() else None


def latest_report(nightly_dir: Path, source: str) -> tuple[NightlyRun, ReportDocument] | None:
    """The newest successful run that has this source's report. Folder names sort by time."""
    if not nightly_dir.is_dir():
        return None
    for folder in sorted((p for p in nightly_dir.iterdir() if p.is_dir()), reverse=True):
        run_file, report_file = folder / "run.json", folder / f"{source}.json"
        if not (run_file.exists() and report_file.exists()):
            continue
        run = _read(run_file, NightlyRun)
        if run.status == "success":
            return run, _read(report_file, ReportDocument)
    return None
