"""Read which quota a 429 hit, from the API's QuotaFailure details."""

import re

from google.genai import errors


def _details(exc: BaseException) -> list[dict]:
    details = getattr(exc, "details", None)
    return details.get("error", {}).get("details", []) if isinstance(details, dict) else []


def quota_ids(exc: BaseException) -> list[str]:
    return [
        str(v.get("quotaId", ""))
        for item in _details(exc)
        for v in item.get("violations", []) or []
        if isinstance(v, dict)
    ]


def is_daily_quota(exc: BaseException) -> bool:
    """True when the key is out for the day; waiting a minute will not help."""
    if not isinstance(exc, errors.APIError) or exc.code != 429:
        return False
    return any("PerDay" in q for q in quota_ids(exc))


def retry_delay_hint(exc: BaseException) -> float | None:
    """Read the API's RetryInfo delay (for example "23s"), if it sent one."""
    for item in _details(exc):
        match = re.fullmatch(r"(\d+(?:\.\d+)?)s", str(item.get("retryDelay", "")))
        if match:
            return float(match.group(1))
    return None
