"""Translate between provider-neutral types and google-genai types."""

from google.genai import types

from app.llm.types import LLMRequest, Message, Role, ToolCall, Usage

# Gemini expects function responses on the user side of the conversation.
_ROLES = {Role.USER: "user", Role.MODEL: "model", Role.TOOL: "user"}


def _parts(message: Message) -> list[types.Part]:
    parts: list[types.Part] = []
    if message.text:
        parts.append(types.Part(text=message.text))
    for call in message.tool_calls:
        fn = types.FunctionCall(name=call.name, args=call.args, id=call.call_id)
        parts.append(types.Part(function_call=fn, thought_signature=call.signature))
    for result in message.tool_results:
        fr = types.FunctionResponse(name=result.name, response=result.content, id=result.call_id)
        parts.append(types.Part(function_response=fr))
    return parts


def to_contents(messages: list[Message]) -> list[types.Content]:
    return [types.Content(role=_ROLES[m.role], parts=_parts(m)) for m in messages]


def to_config(request: LLMRequest) -> types.GenerateContentConfig:
    tools = None
    if request.tools:
        declarations = [
            types.FunctionDeclaration(
                name=t.name, description=t.description, parameters_json_schema=t.parameters
            )
            for t in request.tools
        ]
        tools = [types.Tool(function_declarations=declarations)]
    return types.GenerateContentConfig(
        system_instruction=request.system,
        tools=tools,
        temperature=request.temperature,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )


def _usage(meta: types.GenerateContentResponseUsageMetadata | None) -> Usage:
    if meta is None:
        return Usage()
    return Usage(
        prompt_tokens=meta.prompt_token_count or 0,
        output_tokens=meta.candidates_token_count or 0,
        thinking_tokens=meta.thoughts_token_count or 0,
        total_tokens=meta.total_token_count or 0,
    )


def from_response(raw: types.GenerateContentResponse) -> tuple[str, list[ToolCall], Usage]:
    texts: list[str] = []
    calls: list[ToolCall] = []
    content = raw.candidates[0].content if raw.candidates else None
    for part in content.parts or [] if content else []:
        fc = part.function_call
        if fc and fc.name:
            sig = part.thought_signature
            calls.append(ToolCall(name=fc.name, args=fc.args or {}, call_id=fc.id, signature=sig))
        elif part.text and not part.thought:
            texts.append(part.text)
    return "".join(texts), calls, _usage(raw.usage_metadata)
