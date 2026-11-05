"""SQLite connection for the reporting database. The schema lives in app/reports/sql."""

import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "reports" / "sql" / "schema.sql"


def connect(path: Path | str) -> sqlite3.Connection:
    """Open the database, turn on foreign keys and apply the schema (idempotent)."""
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return conn
