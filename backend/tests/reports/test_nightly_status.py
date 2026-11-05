import pytest

from app.reports.nightly_status import NightlyStatusError, latest_report, read_last_run
from tests.reports.nightly_files import write_run


def test_no_runs_yet(tmp_path):
    assert read_last_run(tmp_path) is None
    assert latest_report(tmp_path / "missing", "project") is None


def test_last_run_is_the_latest_even_when_failed(tmp_path):
    write_run(tmp_path, "2026-11-04_010000", project=2)
    write_run(tmp_path, "2026-11-05_010000", status="failed")
    run = read_last_run(tmp_path)
    assert (run.run_id, run.status, run.failed_step) == ("2026-11-05_010000", "failed", "extract")


def test_latest_report_skips_failed_runs(tmp_path):
    write_run(tmp_path, "2026-11-03_010000", project=1)
    write_run(tmp_path, "2026-11-04_010000", project=2, simulated=5)
    write_run(tmp_path, "2026-11-05_010000", status="failed")
    run, doc = latest_report(tmp_path, "project")
    assert (run.run_id, doc.row_counts["followups"]) == ("2026-11-04_010000", 2)
    assert latest_report(tmp_path, "simulated")[1].source == "simulated"


def test_corrupt_status_file_raises_a_typed_error(tmp_path):
    (tmp_path / "last_run.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(NightlyStatusError):
        read_last_run(tmp_path)
