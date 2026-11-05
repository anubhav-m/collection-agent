r"""Benchmark the extractors on a labelled split and write JSON + Markdown reports.

From backend/:
    .venv\Scripts\python -m app.extraction.benchmark_cli --split dev           # tuning run
    .venv\Scripts\python -m app.extraction.benchmark_cli --split test          # official, once
A test-split run is official: it needs committed extraction code and never overwrites.
"""

import argparse
import asyncio
import sys
from datetime import UTC, datetime

from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.evaluation.git_info import evaluated_code_dirty
from app.extraction.bench_setup import CODE_PATHS, REPORTS_DIR, new_meta
from app.extraction.benchmark import BenchmarkInterruptedError, run_extractor
from app.extraction.dataset import Split, load_set
from app.extraction.llm_extractor import LLMExtractor
from app.extraction.regex_extractor import RegexExtractor
from app.extraction.report import BenchmarkReport, summarise, write_json
from app.extraction.report_md import render_markdown
from app.llm.factory import build_llm


async def main(args: argparse.Namespace) -> int:
    settings, split = get_settings(), Split(args.split)
    official = split is Split.TEST
    base = REPORTS_DIR if official else REPORTS_DIR / "dev"
    json_path, md_path = base / f"{args.name}.json", base / f"{args.name}.md"
    if official and (json_path.exists() or evaluated_code_dirty(CODE_PATHS)):
        print("Official run refused: the report exists or extraction code is uncommitted.")
        return 1
    rows = load_set(split)
    meta = new_meta(args.name, split.value, official, settings, [t.id for t, _ in rows])
    gap = meta.gap_seconds
    print(f"{len(rows)} transcripts: {len(rows)} LLM calls on {meta.model}, {gap} s apart")
    regex, llm = RegexExtractor(), LLMExtractor(build_llm(settings), use_cache=False)
    try:
        results = [summarise("regex", await run_extractor(regex, rows))]
        results.append(summarise("llm", await run_extractor(llm, rows, gap_seconds=gap)))
    except BenchmarkInterruptedError as exc:
        print(f"STOPPED, nothing written: {exc}")
        return 2
    meta.finished_at = datetime.now(UTC)
    report = BenchmarkReport(meta=meta, results=results)
    write_json(json_path, report)
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"saved {json_path}")
    return 0


def cli() -> None:
    parser = argparse.ArgumentParser(description="Benchmark the promise extractors.")
    parser.add_argument("--split", choices=[s.value for s in Split], required=True)
    parser.add_argument("--name", help="Report name (defaults to the split)")
    args = parser.parse_args()
    args.name = args.name or args.split
    configure_logging(get_settings().log_level)
    sys.exit(asyncio.run(main(args)))


if __name__ == "__main__":
    cli()
