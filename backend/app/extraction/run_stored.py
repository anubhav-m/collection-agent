r"""Extract promised payments from every stored conversation and save them to MongoDB.

From backend/:  .venv\Scripts\python -m app.extraction.run_stored [--extractor llm|regex]
Writes one `extractions` document per conversation and extractor, and a run summary to
reports/extraction/stored_run_<extractor>.json.
"""

import argparse
import asyncio
import json
import sys

from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.db.conversations import MongoEventRepo
from app.db.extractions import MongoConversationLister, MongoExtractionRepo
from app.db.indexes import ensure_indexes
from app.db.mongo import MongoDatabase
from app.extraction.bench_setup import REPORTS_DIR, pacing_gap
from app.extraction.benchmark import BenchmarkInterruptedError
from app.extraction.interface import Extractor
from app.extraction.llm_extractor import LLMExtractor
from app.extraction.pipeline import extract_stored
from app.extraction.regex_extractor import RegexExtractor
from app.llm.factory import build_llm

# Chosen from reports/extraction/test.md: equal accuracy, but rules miss unseen phrasings.
DEFAULT_EXTRACTOR = "llm"


async def main(name: str) -> int:
    settings = get_settings()
    mongo = MongoDatabase(
        settings.mongodb_uri.get_secret_value(), settings.mongodb_db, settings.mongodb_timeout_ms
    )
    use_llm = name == "llm"
    extractor: Extractor = LLMExtractor(build_llm(settings)) if use_llm else RegexExtractor()
    model = settings.gemini_model if use_llm else "none"
    gap = pacing_gap(settings.llm_requests_per_minute) if use_llm else 0.0
    try:
        await ensure_indexes(mongo.db)
        summary = await extract_stored(
            extractor, MongoConversationLister(mongo.db), MongoEventRepo(mongo.db),
            MongoExtractionRepo(mongo.db), model=model, gap_seconds=gap,
        )  # fmt: skip
    except BenchmarkInterruptedError as exc:
        print(f"STOPPED: {exc}. Results saved so far are kept; rerun after the quota resets.")
        return 2
    finally:
        await mongo.close()
    rows = [r.model_dump(mode="json") for r in summary.saved]
    out = {"extractor": name, "model": model, "saved": rows, "skipped": summary.skipped}
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"stored_run_{name}.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"saved {len(rows)} extractions to MongoDB, skipped {len(summary.skipped)}")
    return 0


def cli() -> None:
    parser = argparse.ArgumentParser(description="Extract promises from stored conversations.")
    parser.add_argument("--extractor", choices=["regex", "llm"], default=DEFAULT_EXTRACTOR)
    args = parser.parse_args()
    configure_logging(get_settings().log_level)
    sys.exit(asyncio.run(main(args.extractor)))


if __name__ == "__main__":
    cli()
