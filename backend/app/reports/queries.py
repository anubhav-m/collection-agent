"""Run the .sql reports in app/reports/sql against the reporting database."""

import sqlite3
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from app.reports.rows import Source

SQL_DIR = Path(__file__).resolve().parent / "sql"
REPORT_NAMES = (
    "followups",
    "kept_rate_lender",
    "kept_rate_weekly",
    "escalation_reasons",
    "overdue_ranking",
)


@dataclass(frozen=True)
class ReportParams:
    as_of: date
    source: Source
    window_days: int = 3  # "due soon" horizon for follow-ups
    top_n: int = 10  # borrowers kept per lender in the overdue ranking
    top_reasons: int = 3  # escalation reasons kept per lender (ties share a rank)

    def bind(self) -> dict[str, Any]:
        return asdict(self) | {"as_of": self.as_of.isoformat()}


def run_report(conn: sqlite3.Connection, name: str, params: ReportParams) -> list[dict[str, Any]]:
    if name not in REPORT_NAMES:
        raise KeyError(f"unknown report {name!r}")
    sql = (SQL_DIR / f"{name}.sql").read_text(encoding="utf-8")
    return [dict(row) for row in conn.execute(sql, params.bind())]


def run_all(conn: sqlite3.Connection, params: ReportParams) -> dict[str, list[dict[str, Any]]]:
    return {name: run_report(conn, name, params) for name in REPORT_NAMES}
