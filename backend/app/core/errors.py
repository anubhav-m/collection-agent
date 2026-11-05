"""Typed application errors. Messages here are safe to show to clients."""


class AppError(Exception):
    status_code = 500
    code = "internal_error"
    public_message = "Something went wrong. Please try again."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.public_message)
        self.message = message or self.public_message


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"
    public_message = "The requested resource was not found."


class ValidationFailedError(AppError):
    status_code = 422
    code = "validation_failed"
    public_message = "The request was not valid."


class DatabaseUnavailableError(AppError):
    status_code = 503
    code = "database_unavailable"
    public_message = "The database is not available right now."


class LLMUnavailableError(AppError):
    status_code = 503
    code = "llm_unavailable"
    public_message = "The assistant is not available right now."


class ConfigurationError(AppError):
    code = "configuration_error"
    public_message = "The service is not configured correctly."


class RateLimitedError(AppError):
    status_code = 429
    code = "rate_limited"
    public_message = "You're sending messages quickly. Please wait a moment and try again."

    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__()
        self.retry_after_seconds = retry_after_seconds


class DailyLimitReachedError(AppError):
    status_code = 429
    code = "daily_limit_reached"
    public_message = (
        "This demo has reached its daily limit on assistant replies. "
        "Please come back tomorrow. The results and reports views still work."
    )
