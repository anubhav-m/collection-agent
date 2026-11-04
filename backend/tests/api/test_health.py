import httpx
import pytest

from app.core.settings import Settings, get_settings
from app.main import create_app

SECRET_KEY = "unit-test-secret-key"
SECRET_URI = "mongodb://user:hunter2@db.example.invalid"


class FakeMongo:
    def __init__(self, healthy: bool) -> None:
        self.healthy = healthy

    async def ping(self) -> bool:
        return self.healthy


async def call_health(healthy: bool) -> httpx.Response:
    app = create_app()
    app.state.mongo = FakeMongo(healthy)
    settings = Settings(_env_file=None, gemini_api_key_1=SECRET_KEY, mongodb_uri=SECRET_URI)
    app.dependency_overrides[get_settings] = lambda: settings
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get("/health")


async def test_health_reports_connected_database():
    response = await call_health(healthy=True)
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "collections-agent",
        "database": "connected",
        "llm_configured": True,
    }


async def test_health_reports_outage_with_503():
    response = await call_health(healthy=False)
    assert response.status_code == 503
    assert response.json()["database"] == "disconnected"


@pytest.mark.parametrize("healthy", [True, False])
async def test_health_never_exposes_secrets(healthy):
    response = await call_health(healthy)
    assert SECRET_KEY not in response.text
    assert "hunter2" not in response.text
    assert "x-request-id" in response.headers
