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
