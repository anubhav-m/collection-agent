from app.agent.loop import FALLBACK_MESSAGE, LIMIT_MESSAGE, MAX_TOOL_ITERATIONS, run_turn
from app.core.errors import LLMUnavailableError
from app.llm.fake import FakeLLM, text_reply, tool_reply
from app.llm.types import Message, Role
from tests.fakes.context import make_ctx

HISTORY = [Message(role=Role.USER, text="hi")]


async def test_turn_is_capped_at_five_tool_iterations():
    llm = FakeLLM([tool_reply("get_account") for _ in range(10)])
    ctx = await make_ctx(verified_as="BRW-002")
    turn = await run_turn(llm, ctx, HISTORY)
    assert (turn.reply, turn.outcome) == (LIMIT_MESSAGE, "iteration_limit")
    assert len(llm.requests) == MAX_TOOL_ITERATIONS
    results = [e for e in ctx.repos.events.items if e.kind == "tool_result"]
    # Four calls ran; the fifth request was recorded as skipped, not executed.
    assert [r.accepted for r in results] == [True] * 4 + [False]
    assert results[-1].reason == "tool_iteration_limit"


async def test_llm_failure_returns_safe_fallback():
    ctx = await make_ctx()
    turn = await run_turn(FakeLLM([LLMUnavailableError()]), ctx, HISTORY)
    assert (turn.reply, turn.outcome) == (FALLBACK_MESSAGE, "llm_error")


async def test_unexpected_llm_error_also_falls_back():
    ctx = await make_ctx()
    turn = await run_turn(FakeLLM([RuntimeError("boom with secret detail")]), ctx, HISTORY)
    assert turn.reply == FALLBACK_MESSAGE and "secret" not in turn.reply


async def test_blank_model_reply_is_never_returned():
    ctx = await make_ctx()
    turn = await run_turn(FakeLLM([text_reply("   ")]), ctx, HISTORY)
    assert turn.reply == LIMIT_MESSAGE


async def test_tool_results_are_sent_back_to_the_model():
    llm = FakeLLM([tool_reply("get_account"), text_reply("Your balance is 850.50.")])
    ctx = await make_ctx(verified_as="BRW-002")
    turn = await run_turn(llm, ctx, HISTORY)
    assert turn.outcome == "answered"
    sent = llm.requests[1].messages[-1]
    assert sent.role is Role.TOOL and sent.tool_results[0].content["ok"] is True
    assert "identity verified=yes" in llm.requests[0].system
