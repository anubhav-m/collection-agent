"""Scripted LLM for tests. Never touches the network or spends quota."""

from typing import Any

from app.llm.types import LLMRequest, LLMResponse, ToolCall, Usage


def text_reply(text: str) -> LLMResponse:
    return LLMResponse(text=text, usage=Usage(prompt_tokens=1, output_tokens=1, total_tokens=2))


def tool_reply(name: str, **args: Any) -> LLMResponse:
    return LLMResponse(tool_calls=[ToolCall(name=name, args=args, call_id=f"call-{name}")])


class FakeLLM:
    def __init__(self, replies: list[LLMResponse | Exception] | None = None) -> None:
        self._replies = list(replies or [])
        self.requests: list[LLMRequest] = []

    def queue(self, *replies: LLMResponse | Exception) -> None:
        self._replies.extend(replies)

    async def generate(self, request: LLMRequest, *, use_cache: bool = True) -> LLMResponse:
        self.requests.append(request)
        if not self._replies:
            raise AssertionError("FakeLLM has no scripted reply left")
        reply = self._replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply.model_copy(update={"model": reply.model or "fake-llm"})
