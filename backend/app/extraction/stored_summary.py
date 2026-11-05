"""Write the summary file of one stored-conversation extraction run."""

import json
from pathlib import Path

from app.extraction.pipeline import PipelineSummary


def write_summary(path: Path, extractor: str, model: str, summary: PipelineSummary) -> None:
    rows = [r.model_dump(mode="json") for r in summary.saved]
    out = {"extractor": extractor, "model": model, "saved": rows, "skipped": summary.skipped}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
