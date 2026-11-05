"""Shared error reporting for command-line entry points."""


def database_unavailable(exc: Exception) -> int:
    """Print a safe one-line failure and return the exit code. The exception text can
    include the database host, so only its type is shown."""
    print(f"FAILED: database unavailable ({type(exc).__name__})")
    return 1
