"""Turn saved report files into the shapes the results view shows."""

from pathlib import Path

from pydantic import ValidationError

from app.reports.published_results import (
    EVALUATION_RUNS,
    EXTRACTION_SPLIT,
    EvaluationRun,
    ExtractionRun,
    ResultsUnreadableError,
    load_json,
    repo_path,
)


def evaluation_runs(reports_dir: Path) -> list[EvaluationRun]:
    runs = []
    for name in EVALUATION_RUNS:
        path = reports_dir / "evaluation" / f"{name}.json"
        if (data := load_json(path)) is None:
            continue
        meta, metrics = data.get("meta", {}), data.get("metrics", {})
        fields = {
            "run_name": meta.get("run_name"),
            "model": meta.get("model"),
            "git_commit": str(meta.get("git_commit", ""))[:10],
            "finished_at": meta.get("finished_at"),
            "llm_calls": metrics.get("llm_usage", {}).get("calls"),
            "report_path": repo_path(path.with_suffix(".md"), reports_dir),
        }
        runs.append(_validate(EvaluationRun, metrics | fields, path))
    return runs


def extraction_runs(reports_dir: Path) -> list[ExtractionRun]:
    path = reports_dir / "extraction" / f"{EXTRACTION_SPLIT}.json"
    if (data := load_json(path)) is None:
        return []
    meta = data.get("meta", {})
    return [
        _validate(
            ExtractionRun,
            r.get("metrics", {})
            | {
                "extractor": r.get("extractor"),
                "split": meta.get("split"),
                "model": meta.get("model") if r.get("extractor") == "llm" else None,
                "report_path": repo_path(path.with_suffix(".md"), reports_dir),
            },
            path,
        )
        for r in data.get("results", [])
    ]


def _validate[M: EvaluationRun | ExtractionRun](model: type[M], data: dict, path: Path) -> M:
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise ResultsUnreadableError(f"{path.name}: unexpected shape") from exc
