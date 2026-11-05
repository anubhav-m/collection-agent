"""Saved evaluation and extraction results, read from the committed report files."""

import asyncio

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.deps import SettingsDep
from app.core.errors import AppError
from app.reports.published_readers import evaluation_runs, extraction_runs
from app.reports.published_results import EvaluationRun, ExtractionRun, ResultsUnreadableError

router = APIRouter(tags=["results"])


class ResultsFilesUnreadableError(AppError):
    code = "results_unreadable"
    public_message = "The saved results files could not be read."


class ResultsResponse(BaseModel):
    evaluation: list[EvaluationRun]
    extraction: list[ExtractionRun]


def _read_all(settings: SettingsDep) -> ResultsResponse:
    return ResultsResponse(
        evaluation=evaluation_runs(settings.reports_dir),
        extraction=extraction_runs(settings.reports_dir),
    )


@router.get("/results", response_model=ResultsResponse)
async def get_results(settings: SettingsDep) -> ResultsResponse:
    try:
        return await asyncio.to_thread(_read_all, settings)
    except ResultsUnreadableError as exc:
        raise ResultsFilesUnreadableError() from exc
