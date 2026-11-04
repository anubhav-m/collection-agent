import httpx
import pytest
from fastapi import FastAPI

from app.core.errors import NotFoundError
from app.core.handlers import register_exception_handlers
from app.core.request_id import RequestIdMiddleware


def build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)

    @app.get("/missing")
    async def missing():
        raise NotFoundError()

    @app.get("/boom")
    async def boom():
        raise RuntimeError("secret detail token=abc")

    return app


@pytest.fixture
async def client():
    # raise_app_exceptions=False lets Starlette's server-error path answer like production.
    transport = httpx.ASGITransport(app=build_app(), raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def test_app_error_maps_to_status_and_code(client):
    response = await client.get("/missing", headers={"x-request-id": "req-123"})
    assert response.status_code == 404
    assert response.json()["error"] == {
        "code": "not_found",
        "message": "The requested resource was not found.",
        "request_id": "req-123",
    }
    assert response.headers["x-request-id"] == "req-123"


async def test_unexpected_error_is_generic_and_hides_details(client):
    response = await client.get("/boom")
    assert response.status_code == 500
    body = response.json()["error"]
    assert body["code"] == "internal_error"
    assert "secret" not in response.text
    assert len(body["request_id"]) == 32


async def test_unsafe_request_id_is_replaced(client):
    response = await client.get("/missing", headers={"x-request-id": "bad id\nx"})
    assert response.headers["x-request-id"] != "bad id\nx"
    assert len(response.headers["x-request-id"]) == 32
