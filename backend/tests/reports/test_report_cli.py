import json
from datetime import date

from app.db.sqlite import connect
from app.reports.loader import load_dataset
from app.reports.report_cli import main
from tests.reports.fixture_rows import project_fixture, simulated_fixture

AS_OF = date(2026, 3, 10)


def test_missing_database_fails_without_writing(tmp_path, capsys):
    assert main(AS_OF, tmp_path / "out", tmp_path / "none.sqlite3") == 1
    assert "FAILED" in capsys.readouterr().out
    assert not (tmp_path / "out").exists()


def test_writes_both_sources_and_summary(tmp_path):
    db_path = tmp_path / "r.sqlite3"
    conn = connect(db_path)
    load_dataset(conn, project_fixture())
    load_dataset(conn, simulated_fixture())
    conn.close()
    out = tmp_path / "run"
    assert main(AS_OF, out, db_path) == 0
    project = json.loads((out / "project.json").read_text(encoding="utf-8"))
    simulated = json.loads((out / "simulated.json").read_text(encoding="utf-8"))
    assert project["row_counts"]["followups"] == 4
    assert simulated["note"].startswith("SIMULATED")
    summary = (out / "summary.md").read_text(encoding="utf-8")
    assert "| Fixture Two | 3 | 2 | 66.7% |" in summary
    assert "Follow-ups: 4 (2 overdue)." in summary
