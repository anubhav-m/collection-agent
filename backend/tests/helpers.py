"""Shared test helpers: fake Gemini SDK pieces and API errors."""

from typing import Any

from google.genai import errors, types


def api_error(code: int, retry_delay: str | None = None) -> errors.APIError:
    details = [{"retryDelay": retry_delay}] if retry_delay else []
    body = {"error": {"code": code, "message": "fake", "status": "FAKE", "details": details}}
    cls = errors.ClientError if code < 500 else errors.ServerError
    return cls(code, body)


def gemini_response(text: str = "", call: dict[str, Any] | None = None):
    parts = [types.Part(text=text)] if text else []
    if call:
        fc = types.FunctionCall(name=call["name"], args=call.get("args"), id="c1")
        parts.append(types.Part(function_call=fc, thought_signature=b"sig"))
    usage = types.GenerateContentResponseUsageMetadata(
        prompt_token_count=10,
        candidates_token_count=4,
        thoughts_token_count=3,
        total_token_count=17,
    )
    content = types.Content(role="model", parts=parts)
    return types.GenerateContentResponse(
        candidates=[types.Candidate(content=content)], usage_metadata=usage
    )


class _FakeModels:
    def __init__(self, outcomes: list) -> None:
        self.outcomes = outcomes
        self.calls = 0

    async def generate_content(self, **kwargs: Any):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeGenaiClient:
    """Stands in for genai.Client; only `.aio.models.generate_content` is used."""

    def __init__(self, *outcomes: Any) -> None:
        self.models = _FakeModels(list(outcomes))
        self.aio = self
