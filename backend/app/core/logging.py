"""Structured JSON logging that tags every record with request context."""

import json
import logging
from datetime import UTC, datetime

from app.core.context import conversation_id_var, request_id_var

_RESERVED = set(logging.makeLogRecord({}).__dict__) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_var.get(),
            "conversation_id": conversation_id_var.get(),
        }
        # Fields passed through `extra=` become structured keys.
        payload |= {k: v for k, v in record.__dict__.items() if k not in _RESERVED}
        if record.exc_info:
            payload["exc_type"] = record.exc_info[0].__name__ if record.exc_info[0] else None
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())
    # The SDK's HTTP client logs full URLs; keep it quiet.
    logging.getLogger("httpx").setLevel(logging.WARNING)
