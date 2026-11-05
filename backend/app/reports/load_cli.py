r"""Load project data from MongoDB and the seeded simulated history into SQLite.
From backend/:  .venv\Scripts\python -m app.reports.load_cli --as-of 2026-11-05 [--out DIR]"""

import argparse
import asyncio
import json
import sqlite3
import sys
from contextlib import closing
from datetime import date
from pathlib import Path

from pymongo.errors import PyMongoError

from app.core.cli import database_unavailable
from app.core.logging import configure_logging
from app.core.settings import Settings, get_settings
from app.db.mongo import mongo_from_settings
from app.db.report_source import ProjectSnapshot, read_project_snapshot
from app.db.sqlite import connect
from app.extraction.run_stored import DEFAULT_EXTRACTOR
from app.reports.loader import load_dataset
from app.reports.project_source import build_project_dataset
from app.reports.simulate import simulate


async def read_snapshot(settings: Settings, extractor: str) -> ProjectSnapshot:
    mongo = mongo_from_settings(settings)
    try:
        return await read_project_snapshot(mongo.db, extractor)
    finally:
        await mongo.close()


def main(as_of: date, extractor: str, out: Path | None) -> int:
    settings = get_settings()
    try:
        snapshot = asyncio.run(read_snapshot(settings, extractor))
    except PyMongoError as exc:
        return database_unavailable(exc)
    try:
        with closing(connect(settings.reports_db_path)) as conn:
            counts = {
                "project": load_dataset(conn, build_project_dataset(snapshot)),
                "simulated": load_dataset(conn, simulate(as_of)),
            }
    except (sqlite3.Error, OSError) as exc:
        print(f"FAILED: load error ({type(exc).__name__}: {exc})")
        return 1
    print(json.dumps(counts))
    if out:
        out.mkdir(parents=True, exist_ok=True)
        summary = {"as_of": as_of.isoformat(), "extractor": extractor, "rows": counts}
        (out / "load.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return 0


def cli() -> None:
    parser = argparse.ArgumentParser(description="Load the reporting database.")
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--extractor", choices=["regex", "llm"], default=DEFAULT_EXTRACTOR)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    configure_logging(get_settings().log_level)
    sys.exit(main(args.as_of, args.extractor, args.out))


if __name__ == "__main__":
    cli()
