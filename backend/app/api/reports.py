"""Latest nightly report data. Reads files written by the nightly job; never runs SQL."""

import asyncio
from typing import Literal

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.core.deps import SettingsDep
from app.core.errors import AppError, NotFoundError
from app.reports.nightly_status import NightlyStatusError, ReportDocument, latest_report

router = APIRouter(tags=["reports"])


class ReportsUnreadableError(AppError):
    code = "reports_unreadable"
    public_message = "The latest report files could not be read."


class ReportsResponse(BaseModel):
    run_id: str
    run_finished_at: str
    report: ReportDocument


@router.get("/reports", response_model=ReportsResponse)
async def get_reports(
    settings: SettingsDep, source: Literal["project", "simulated"] = Query("project")
) -> ReportsResponse:
    try:
        found = await asyncio.to_thread(latest_report, settings.nightly_dir, source)
    except NightlyStatusError as exc:
        raise ReportsUnreadableError() from exc
    if found is None:
        raise NotFoundError("No successful nightly run has produced reports yet.")
    run, document = found
    return ReportsResponse(
        run_id=run.run_id, run_finished_at=run.finished_at.isoformat(), report=document
    )
