from app.llm.gemini_mapping import from_response, to_config, to_contents
from app.llm.types import LLMRequest, Message, Role, ToolCall, ToolResult, ToolSpec
from tests.helpers import gemini_response


def test_to_contents_maps_roles_and_tool_parts():
    messages = [
        Message(role=Role.USER, text="hi"),
        Message(role=Role.MODEL, tool_calls=[ToolCall(name="t", args={"a": 1}, signature=b"s")]),
        Message(role=Role.TOOL, tool_results=[ToolResult(name="t", content={"ok": True})]),
    ]
    contents = to_contents(messages)
    assert [c.role for c in contents] == ["user", "model", "user"]
    call_part = contents[1].parts[0]
    assert call_part.function_call.args == {"a": 1}
    assert call_part.thought_signature == b"s"
    assert contents[2].parts[0].function_response.response == {"ok": True}


def test_to_config_declares_tools_and_disables_auto_calling():
    spec = ToolSpec(name="t", description="d", parameters={"type": "object"})
    config = to_config(LLMRequest(messages=[], system="be brief", tools=[spec]))
    assert config.system_instruction == "be brief"
    assert config.tools[0].function_declarations[0].name == "t"
    assert config.automatic_function_calling.disable is True
    assert to_config(LLMRequest(messages=[])).tools is None


def test_from_response_reads_text_calls_and_usage():
    raw = gemini_response("hello", call={"name": "t", "args": {"x": "y"}})
    text, calls, usage = from_response(raw)
    assert text == "hello"
    assert calls[0].name == "t" and calls[0].args == {"x": "y"}
    assert calls[0].signature == b"sig"
    assert (usage.prompt_tokens, usage.output_tokens, usage.thinking_tokens) == (10, 4, 3)


def test_from_response_handles_empty_candidates():
    from google.genai import types

    text, calls, usage = from_response(types.GenerateContentResponse())
    assert (text, calls, usage.total_tokens) == ("", [], 0)


def test_to_config_requests_json_only_when_a_schema_is_given():
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
    config = to_config(LLMRequest(messages=[], response_schema=schema))
    assert config.response_mime_type == "application/json"
    assert config.response_json_schema == schema
    plain = to_config(LLMRequest(messages=[]))
    assert plain.response_mime_type is None and plain.response_json_schema is None
