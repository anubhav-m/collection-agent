r"""Run every SQL report for both sources and write them to a nightly run folder.

From backend/:  .venv\Scripts\python -m app.reports.report_cli --as-of 2026-11-05 --out DIR
"""

import argparse
import sqlite3
import sys
from contextlib import closing
from datetime import date
from pathlib import Path

from app.core.settings import get_settings
from app.db.sqlite import connect
from app.reports.output import report_document, summary_markdown, write_json
from app.reports.queries import ReportParams, run_all


def main(as_of: date, out: Path, db_path: Path) -> int:
    if not db_path.exists():
        print(f"FAILED: reporting database not found at {db_path.name}; run the load first")
        return 1
    documents = []
    try:
        with closing(connect(db_path)) as conn:
            for source in ("project", "simulated"):
                params = ReportParams(as_of=as_of, source=source)
                documents.append(report_document(params, run_all(conn, params)))
    except (sqlite3.Error, OSError) as exc:
        print(f"FAILED: report query error ({type(exc).__name__}: {exc})")
        return 1
    for doc in documents:
        write_json(out / f"{doc['source']}.json", doc)
        print(f"{doc['source']}: {doc['row_counts']}")
    (out / "summary.md").write_text(summary_markdown(documents), encoding="utf-8")
    return 0


def cli() -> None:
    parser = argparse.ArgumentParser(description="Write the nightly SQL reports.")
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    sys.exit(main(args.as_of, args.out, get_settings().reports_db_path))


if __name__ == "__main__":
    cli()
