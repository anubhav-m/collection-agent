"""Health check route. Reports status only, never connection details."""

from typing import Literal

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app.core.deps import MongoDep, SettingsDep

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    app: str
    database: Literal["connected", "disconnected"]
    llm_configured: bool


@router.get("/health", response_model=HealthResponse)
async def health(mongo: MongoDep, settings: SettingsDep, response: Response) -> HealthResponse:
    connected = await mongo.ping()
    if not connected:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(
        status="ok" if connected else "degraded",
        app=settings.app_name,
        database="connected" if connected else "disconnected",
        llm_configured=bool(settings.gemini_api_keys),
    )
