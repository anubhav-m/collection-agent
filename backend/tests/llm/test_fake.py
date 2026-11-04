import pytest

from app.core.errors import LLMUnavailableError
from app.llm.fake import FakeLLM, text_reply, tool_reply
from app.llm.types import LLMRequest, Message, Role

REQUEST = LLMRequest(messages=[Message(role=Role.USER, text="hi")])


async def test_returns_scripted_replies_in_order_and_records_requests():
    llm = FakeLLM([tool_reply("lookup", account_id="ACC-1"), text_reply("done")])
    first = await llm.generate(REQUEST)
    second = await llm.generate(REQUEST)
    assert first.tool_calls[0].args == {"account_id": "ACC-1"}
    assert second.text == "done" and second.model == "fake-llm"
    assert llm.requests == [REQUEST, REQUEST]


async def test_scripted_exception_is_raised():
    llm = FakeLLM()
    llm.queue(LLMUnavailableError())
    with pytest.raises(LLMUnavailableError):
        await llm.generate(REQUEST)


async def test_running_out_of_replies_fails_loudly():
    with pytest.raises(AssertionError, match="no scripted reply"):
        await FakeLLM().generate(REQUEST)
