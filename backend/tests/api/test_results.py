import json

import httpx

from app.core.settings import Settings, get_settings
from app.main import create_app


async def get_results(reports_dir) -> httpx.Response:
    app = create_app()
    settings = Settings(_env_file=None, mongodb_uri="mongodb://x.invalid", reports_dir=reports_dir)
    app.dependency_overrides[get_settings] = lambda: settings
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get("/results")


async def test_results_reads_the_committed_reports():
    response = await get_results(Settings(_env_file=None, mongodb_uri="x").reports_dir)
    assert response.status_code == 200
    body = response.json()
    latest = next(r for r in body["evaluation"] if r["run_name"] == "latest")
    assert latest["scenario_count"] == 38 and latest["report_path"].endswith("latest.md")
    llm = next(r for r in body["extraction"] if r["extractor"] == "llm")
    assert llm["split"] == "test" and set(llm["entities"]) == {"promise_made", "amount", "date"}
    regex = next(r for r in body["extraction"] if r["extractor"] == "regex")
    assert regex["model"] is None


async def test_results_empty_when_no_reports(tmp_path):
    body = (await get_results(tmp_path)).json()
    assert body == {"evaluation": [], "extraction": []}


async def test_results_corrupt_file_is_a_clean_error(tmp_path):
    (tmp_path / "evaluation").mkdir()
    (tmp_path / "evaluation" / "latest.json").write_text("{not json")
    response = await get_results(tmp_path)
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "results_unreadable"


async def test_results_unexpected_shape_is_a_clean_error(tmp_path):
    (tmp_path / "evaluation").mkdir()
    (tmp_path / "evaluation" / "baseline.json").write_text(json.dumps({"meta": {}}))
    response = await get_results(tmp_path)
    assert response.json()["error"]["code"] == "results_unreadable"
