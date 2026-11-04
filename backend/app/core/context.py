"""Per-request context values shared by logging and handlers."""

from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
conversation_id_var: ContextVar[str] = ContextVar("conversation_id", default="-")
