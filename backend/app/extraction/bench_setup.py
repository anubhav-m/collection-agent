"""Where benchmark reports go, how LLM calls are spaced, and the run's recorded setup."""

from datetime import UTC, datetime

from app.core.settings import PROJECT_ROOT, Settings
from app.evaluation.git_info import current_commit
from app.extraction.report import BenchmarkMeta

REPORTS_DIR = PROJECT_ROOT / "reports" / "extraction"
# Changes here change extraction results, so an official run needs them committed.
CODE_PATHS = ["backend/app/extraction", "backend/app/llm", "backend/data/extraction"]


def pacing_gap(requests_per_minute: int) -> float:
    """Seconds between LLM calls: just over the limit's spacing, so no call ever queues."""
    return round(60 / requests_per_minute + 0.5, 2)


def new_meta(
    name: str, split: str, official: bool, settings: Settings, ids: list[str]
) -> BenchmarkMeta:
    return BenchmarkMeta(
        run_name=name,
        split=split,
        official=official,
        model=settings.gemini_model,
        git_commit=current_commit(CODE_PATHS),
        requests_per_minute=settings.llm_requests_per_minute,
        gap_seconds=pacing_gap(settings.llm_requests_per_minute),
        transcript_ids=ids,
        started_at=datetime.now(UTC),
    )
