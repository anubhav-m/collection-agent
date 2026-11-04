import httpx
from fastapi import FastAPI, HTTPException

from app.core.handlers import register_exception_handlers


def build_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/items/{item_id}")
    async def item(item_id: int):
        return {"id": item_id}

    @app.get("/forbidden")
    async def forbidden():
        raise HTTPException(status_code=403, detail="internal reason")

    return app


async def get(path: str) -> httpx.Response:
    transport = httpx.ASGITransport(app=build_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get(path)


async def test_unknown_route_uses_standard_error_shape():
    response = await get("/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


async def test_validation_error_uses_standard_error_shape():
    response = await get("/items/not-a-number")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_failed"


async def test_http_exception_keeps_status_but_hides_detail():
    response = await get("/forbidden")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "http_error"
    assert "internal reason" not in response.text
