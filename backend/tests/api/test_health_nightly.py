from tests.api.test_health import EMPTY_NIGHTLY, call_health
from tests.reports.nightly_files import write_run


async def test_health_reports_failed_nightly_run_but_stays_ok(tmp_path):
    write_run(tmp_path, "2026-11-05_010000", status="failed")
    response = await call_health(healthy=True, nightly_dir=tmp_path)
    assert response.status_code == 200
    nightly = response.json()["nightly"]
    assert (nightly["status"], nightly["failed_step"]) == ("failed", "extract")


async def test_health_marks_unreadable_nightly_status(tmp_path):
    (tmp_path / "last_run.json").write_text("{", encoding="utf-8")
    response = await call_health(healthy=True, nightly_dir=tmp_path)
    assert response.json()["nightly"] == EMPTY_NIGHTLY | {"status": "unreadable"}


async def test_health_reports_outage_with_503():
    response = await call_health(healthy=False)
    assert response.status_code == 503
    assert response.json()["database"] == "disconnected"
