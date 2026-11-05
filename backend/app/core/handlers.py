"""One exception handler that maps every error to a consistent JSON body."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.core.context import request_id_var
from app.core.errors import AppError, NotFoundError, ValidationFailedError

logger = logging.getLogger(__name__)


def to_app_error(exc: Exception) -> AppError:
    if isinstance(exc, AppError):
        return exc
    if isinstance(exc, RequestValidationError):
        return ValidationFailedError()
    if isinstance(exc, HTTPException):
        error = NotFoundError() if exc.status_code == 404 else AppError("The request failed.")
        error.status_code = exc.status_code
        if exc.status_code not in (404, 500):
            error.code = "http_error"
        return error
    return AppError()


async def handle_error(request: Request, exc: Exception) -> JSONResponse:
    error = to_app_error(exc)
    request_id = getattr(request.state, "request_id", request_id_var.get())
    token = request_id_var.set(request_id)
    log_extra = {"error_code": error.code, "exc_type": type(exc).__name__}
    if error.status_code < 500:
        logger.info("request failed", extra=log_extra | {"path": request.url.path})
    else:
        # Log the type only; tracebacks and messages may carry personal data.
        logger.error("request error", extra=log_extra)
    request_id_var.reset(token)
    body = {"error": {"code": error.code, "message": error.message, "request_id": request_id}}
    retry_after = getattr(error, "retry_after_seconds", None)
    headers = {"Retry-After": str(retry_after)} if retry_after else None
    return JSONResponse(status_code=error.status_code, content=body, headers=headers)


def register_exception_handlers(app: FastAPI) -> None:
    for exc_type in (AppError, HTTPException, RequestValidationError, Exception):
        app.add_exception_handler(exc_type, handle_error)
