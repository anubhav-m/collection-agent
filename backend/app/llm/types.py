"""Provider-neutral request and response types for LLM calls."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Role(StrEnum):
    USER = "user"
    MODEL = "model"
    TOOL = "tool"


class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=lambda: {"type": "object"})


class ToolCall(BaseModel):
    # Signatures are opaque bytes the provider needs back on the next turn.
    model_config = ConfigDict(ser_json_bytes="base64", val_json_bytes="base64")

    name: str
    args: dict[str, Any] = Field(default_factory=dict)
    call_id: str | None = None
    signature: bytes | None = None


class ToolResult(BaseModel):
    name: str
    content: dict[str, Any]
    call_id: str | None = None


class Message(BaseModel):
    role: Role
    text: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    tool_results: list[ToolResult] = Field(default_factory=list)


class LLMRequest(BaseModel):
    messages: list[Message]
    system: str | None = None
    tools: list[ToolSpec] = Field(default_factory=list)
    temperature: float | None = None


class Usage(BaseModel):
    prompt_tokens: int = 0
    output_tokens: int = 0
    thinking_tokens: int = 0
    total_tokens: int = 0


class LLMResponse(BaseModel):
    text: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
    usage: Usage = Field(default_factory=Usage)
    model: str = ""
    latency_ms: float = 0.0
    cached: bool = False
