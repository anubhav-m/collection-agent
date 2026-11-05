"""The benchmark report: one file per run, with metrics and every prediction per extractor."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.extraction.benchmark import Pair
from app.extraction.metrics import compute_metrics
from app.extraction.models import ExtractionOutcome, Label


class BenchmarkMeta(BaseModel):
    run_name: str
    split: str
    official: bool
    model: str
    git_commit: str
    requests_per_minute: int
    gap_seconds: float
    transcript_ids: list[str]
    started_at: datetime
    finished_at: datetime | None = None


class ExtractorResult(BaseModel):
    extractor: str
    metrics: dict[str, Any]
    outcomes: list[ExtractionOutcome]
    labels: list[Label]


class BenchmarkReport(BaseModel):
    meta: BenchmarkMeta
    results: list[ExtractorResult]


def summarise(extractor: str, pairs: list[Pair]) -> ExtractorResult:
    return ExtractorResult(
        extractor=extractor,
        metrics=compute_metrics(pairs),
        outcomes=[o for o, _ in pairs],
        labels=[lb for _, lb in pairs],
    )


def write_json(path: Path, report: BenchmarkReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    os.replace(tmp, path)
