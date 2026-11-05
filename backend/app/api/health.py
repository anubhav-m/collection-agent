"""Health check route. Reports status only, never connection details."""

import asyncio
import logging
from typing import Literal

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app.core.deps import MongoDep, SettingsDep
from app.reports.nightly_status import NightlyStatusError, read_last_run

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


class NightlyHealth(BaseModel):
    status: Literal["success", "failed", "never_run", "unreadable"]
    run_id: str | None = None
    finished_at: str | None = None
    failed_step: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    app: str
    database: Literal["connected", "disconnected"]
    llm_configured: bool
    nightly: NightlyHealth


async def nightly_health(settings: SettingsDep) -> NightlyHealth:
    try:
        run = await asyncio.to_thread(read_last_run, settings.nightly_dir)
    except NightlyStatusError as exc:
        logger.warning("nightly status unreadable", extra={"detail": str(exc)})
        return NightlyHealth(status="unreadable")
    if run is None:
        return NightlyHealth(status="never_run")
    finished = run.finished_at.isoformat()
    return NightlyHealth(
        status=run.status, run_id=run.run_id, finished_at=finished, failed_step=run.failed_step
    )


@router.get("/health", response_model=HealthResponse)
async def health(mongo: MongoDep, settings: SettingsDep, response: Response) -> HealthResponse:
    # A failed nightly run is reported but does not make the API itself unhealthy.
    connected = await mongo.ping()
    if not connected:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(
        status="ok" if connected else "degraded",
        app=settings.app_name,
        database="connected" if connected else "disconnected",
        llm_configured=bool(settings.gemini_api_keys),
        nightly=await nightly_health(settings),
    )
