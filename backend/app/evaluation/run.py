r"""Run the evaluation scenarios against the live model and write JSON + Markdown reports.

From backend/:
    .venv\Scripts\python -m app.evaluation.run --name baseline            # official run
    .venv\Scripts\python -m app.evaluation.run --name dbg --only id1,id2  # debug run
An official run resumes from reports/evaluation/<name>.progress.json if it exists.
"""

import argparse
import asyncio
import sys
from datetime import UTC, datetime

from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.evaluation.environment import REPORTS_DIR, EvalEnvironment
from app.evaluation.metrics import compute_metrics
from app.evaluation.output import paths_for, write_reports
from app.evaluation.progress import ResumeMismatchError, load_or_start
from app.evaluation.results import RunFile
from app.evaluation.run_setup import prepare
from app.evaluation.runner import RunInterruptedError, run_pending


async def main(args: argparse.Namespace) -> int:
    settings = get_settings()
    scenarios, meta = prepare(args.name, args.only, settings.gemini_model)
    paths = paths_for(REPORTS_DIR, args.name, meta.official)
    if meta.official and paths.final_json.exists():
        print(f"{paths.final_json.name} exists; official reports are never overwritten.")
        return 1
    if meta.official and meta.git_dirty:
        print("Commit the agent code and scenarios first: an official run must match its commit.")
        return 1
    try:
        run = load_or_start(paths.progress, meta) if paths.progress else RunFile(meta=meta)
    except ResumeMismatchError as exc:
        print(f"Cannot resume: {exc}")
        return 1
    env = EvalEnvironment(settings)
    try:
        await env.start()
        run = await run_pending(env, scenarios, run, paths.progress)
    except RunInterruptedError as exc:
        print(f"STOPPED: {exc} Rerun the same command after the quota resets to resume.")
        return 2
    finally:
        await env.close()
    run.meta.finished_at = datetime.now(UTC)
    run.metrics = compute_metrics(run.results)
    write_reports(paths, run)
    print(f"task success {run.metrics['task_success_rate']}; saved {paths.final_json}")
    return 0


def cli() -> None:
    parser = argparse.ArgumentParser(description="Run the agent evaluation scenarios.")
    parser.add_argument("--name", required=True, help="Report name, e.g. baseline or latest")
    parser.add_argument("--only", help="Comma-separated scenario ids (debug run)")
    args = parser.parse_args()
    configure_logging(get_settings().log_level)
    sys.exit(asyncio.run(main(args)))


if __name__ == "__main__":
    cli()
