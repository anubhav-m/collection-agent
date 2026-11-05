"""Load one source's rows into SQLite. A load replaces that source's rows in one
transaction, so running it twice gives the same tables and a failed load changes nothing."""

import sqlite3
from dataclasses import astuple, fields

from app.reports.dataset import Dataset


class SourceMismatchError(ValueError):
    pass


def _insert_sql(table: str, row_type: type) -> str:
    columns = [f.name for f in fields(row_type)]
    placeholders = ", ".join("?" for _ in columns)
    return f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"


def load_dataset(conn: sqlite3.Connection, dataset: Dataset) -> dict[str, int]:
    tables = dataset.tables()
    for table, rows in tables:
        if any(row.source != dataset.source for row in rows):
            raise SourceMismatchError(f"{table} has rows from another source")
    with conn:  # commits on success, rolls back on any error
        for table, _ in reversed(tables):  # children first, for foreign keys
            conn.execute(f"DELETE FROM {table} WHERE source = ?", (dataset.source,))
        for table, rows in tables:
            if rows:
                conn.executemany(_insert_sql(table, type(rows[0])), map(astuple, rows))
    return {table: len(rows) for table, rows in tables}


def count_rows(conn: sqlite3.Connection, source: str) -> dict[str, int]:
    names = [table for table, _ in Dataset(source="project").tables()]
    query = "SELECT COUNT(*) FROM {} WHERE source = ?"
    return {t: conn.execute(query.format(t), (source,)).fetchone()[0] for t in names}
