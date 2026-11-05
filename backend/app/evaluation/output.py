"""Where a run's files live, and writing the final JSON and Markdown reports."""

from dataclasses import dataclass
from pathlib import Path

from app.evaluation.progress import save_atomic
from app.evaluation.report_md import render_markdown
from app.evaluation.results import RunFile


@dataclass(frozen=True)
class RunPaths:
    final_json: Path
    final_md: Path
    progress: Path | None  # official runs only; debug runs are short and not resumed


def paths_for(reports_dir: Path, name: str, official: bool) -> RunPaths:
    base = reports_dir if official else reports_dir / "debug"
    progress = base / f"{name}.progress.json" if official else None
    return RunPaths(base / f"{name}.json", base / f"{name}.md", progress)


def write_reports(paths: RunPaths, run: RunFile) -> None:
    save_atomic(paths.final_json, run)
    paths.final_md.write_text(render_markdown(run), encoding="utf-8")
    if paths.progress is not None:
        # The final report holds every result, so the progress file is no longer needed.
        paths.progress.unlink(missing_ok=True)
