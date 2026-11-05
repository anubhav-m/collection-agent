import httpx
from fastapi import FastAPI

from app.api.frontend import mount_frontend


def app_with_dist(dist) -> FastAPI:
    app = FastAPI()

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"from": "api"}

    mount_frontend(app, dist)
    return app


async def test_serves_index_and_assets_and_api_routes_win(tmp_path):
    (tmp_path / "index.html").write_text("<!doctype html><title>demo</title>")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "app.js").write_text("console.log(1)")
    (tmp_path / "ping").write_text("static file with an API name")
    transport = httpx.ASGITransport(app=app_with_dist(tmp_path))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        index = await client.get("/")
        asset = await client.get("/assets/app.js")
        api = await client.get("/ping")
    assert index.status_code == 200 and "demo" in index.text
    assert asset.status_code == 200
    assert api.json() == {"from": "api"}


async def test_missing_build_serves_api_only(tmp_path):
    transport = httpx.ASGITransport(app=app_with_dist(tmp_path))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        index = await client.get("/")
        api = await client.get("/ping")
    assert index.status_code == 404 and api.status_code == 200
