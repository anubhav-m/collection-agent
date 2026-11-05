from datetime import date

import pytest

from app.db.sqlite import connect
from app.reports.loader import load_dataset
from app.reports.queries import ReportParams, run_report
from tests.reports.fixture_rows import AS_OF, project_fixture, simulated_fixture


@pytest.fixture
def db():
    conn = connect(":memory:")
    load_dataset(conn, project_fixture())
    load_dataset(conn, simulated_fixture())
    yield conn
    conn.close()


@pytest.fixture
def report(db):
    def run(name: str, source: str = "project", **overrides):
        values = {"as_of": date.fromisoformat(AS_OF), "source": source} | overrides
        params = ReportParams(**values)
        return run_report(db, name, params)

    return run
