import sqlite3
from dataclasses import replace

import pytest

from app.db.sqlite import connect
from app.reports.loader import SourceMismatchError, count_rows, load_dataset
from tests.reports.fixture_rows import project_fixture, simulated_fixture

EXPECTED = {"lenders": 2, "borrowers": 3, "conversations": 14, "promises": 10}


def snapshot(conn):
    return [conn.execute(f"SELECT * FROM {t} ORDER BY 1").fetchall() for t in EXPECTED]


def test_load_twice_gives_identical_tables(db):
    before = [list(map(tuple, rows)) for rows in snapshot(db)]
    load_dataset(db, project_fixture())
    assert [list(map(tuple, rows)) for rows in snapshot(db)] == before
    assert count_rows(db, "project") == EXPECTED | {"payments": 6, "escalations": 5}


def test_reload_drops_rows_that_left_the_source(db):
    smaller = project_fixture()
    smaller.payments = smaller.payments[:2]
    load_dataset(db, smaller)
    assert count_rows(db, "project")["payments"] == 2


def test_loading_one_source_keeps_the_other(db):
    load_dataset(db, project_fixture())
    assert count_rows(db, "simulated")["promises"] == 1


def test_failed_load_rolls_back(db):
    broken = project_fixture()
    broken.promises.append(replace(broken.promises[0], promise_id="PX", conversation_id="C?"))
    with pytest.raises(sqlite3.IntegrityError):
        load_dataset(db, broken)  # unknown conversation breaks the foreign key
    assert count_rows(db, "project")["promises"] == 10


def test_rows_from_another_source_are_refused():
    conn = connect(":memory:")
    mixed = simulated_fixture()
    mixed.lenders.append(project_fixture().lenders[0])
    with pytest.raises(SourceMismatchError):
        load_dataset(conn, mixed)
    assert count_rows(conn, "simulated")["lenders"] == 0
