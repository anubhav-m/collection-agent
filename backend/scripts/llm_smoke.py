"""One live Gemini call through app.llm, including a function-calling round.

Run from backend/: `python -m scripts.llm_smoke`. Spends 2 requests of quota.
Bypasses the dev cache so the call is always real.
"""

import asyncio
import json

from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.llm.factory import build_llm
from app.llm.types import LLMRequest, Message, Role, ToolSpec

BALANCE_TOOL = ToolSpec(
    name="get_fictional_balance",
    description="Return the balance for a fictional demo account id.",
    parameters={
        "type": "object",
        "properties": {"account_id": {"type": "string"}},
        "required": ["account_id"],
    },
)


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    llm = build_llm(settings)
    plain = await llm.generate(
        LLMRequest(messages=[Message(role=Role.USER, text="Reply with exactly: pong")]),
        use_cache=False,
    )
    tool = await llm.generate(
        LLMRequest(
            messages=[Message(role=Role.USER, text="What is the balance of account ACC-1001?")],
            tools=[BALANCE_TOOL],
        ),
        use_cache=False,
    )
    summary = {
        "plain_text": plain.text.strip(),
        "plain_usage": plain.usage.model_dump(),
        "tool_calls": [c.model_dump(include={"name", "args"}) for c in tool.tool_calls],
        "tool_usage": tool.usage.model_dump(),
        "model": plain.model,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
