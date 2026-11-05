import httpx

from app.core.settings import Settings, get_settings
from app.main import create_app
from tests.reports.nightly_files import write_run


async def get(nightly_dir, path: str) -> httpx.Response:
    app = create_app()
    settings = Settings(_env_file=None, mongodb_uri="mongodb://x.invalid", nightly_dir=nightly_dir)
    app.dependency_overrides[get_settings] = lambda: settings
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get(path)


async def test_reports_returns_latest_successful_run(tmp_path):
    write_run(tmp_path, "2026-11-04_010000", project=3, simulated=7)
    write_run(tmp_path, "2026-11-05_010000", status="failed")
    response = await get(tmp_path, "/reports")
    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == "2026-11-04_010000"
    assert body["report"]["source"] == "project"
    assert len(body["report"]["reports"]["followups"]) == 3


async def test_reports_simulated_source(tmp_path):
    write_run(tmp_path, "2026-11-04_010000", project=3, simulated=7)
    body = (await get(tmp_path, "/reports?source=simulated")).json()
    assert body["report"]["row_counts"] == {"followups": 7}


async def test_reports_404_before_any_run(tmp_path):
    response = await get(tmp_path, "/reports")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


async def test_reports_rejects_unknown_source(tmp_path):
    assert (await get(tmp_path, "/reports?source=other")).status_code == 422


async def test_reports_unreadable_file_is_a_clean_500(tmp_path):
    folder = write_run(tmp_path, "2026-11-04_010000", project=1)
    (folder / "project.json").write_text("{broken", encoding="utf-8")
    response = await get(tmp_path, "/reports")
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "reports_unreadable"
    assert "Traceback" not in response.text
