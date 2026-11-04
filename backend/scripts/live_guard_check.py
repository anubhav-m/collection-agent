r"""Act as a misbehaving model on a live, stored conversation and show the server gate.

Sends forced tool calls through the real executor and MongoDB state. From backend/:
    .venv\Scripts\python -m scripts.live_guard_check CONV-...
"""

import argparse
import asyncio
import json
from datetime import UTC, datetime

from app.agent.executor import execute
from app.agent.turn_events import record_tool_request
from app.core.settings import get_settings
from app.db.mongo import MongoDatabase
from app.db.repositories import mongo_repositories
from app.llm.types import LLMResponse, ToolCall
from app.policy.loader import PolicyStore
from app.tools.base import ToolContext
from scripts.live_chat import REPORTS

FORCED = [
    ToolCall(name="get_account", args={"account_id": "ACC-2002"}, call_id="forced-1"),
    ToolCall(
        name="create_payment_plan",
        args={
            "account_id": "ACC-2002",
            "frequency": "monthly",
            "payments": [3020.0],
            "start_date": datetime.now(UTC).date().isoformat(),
        },
        call_id="forced-2",
    ),
]


async def check(conversation_id: str) -> dict:
    settings = get_settings()
    mongo = MongoDatabase(settings.mongodb_uri.get_secret_value(), settings.mongodb_db)
    try:
        repos = mongo_repositories(mongo.db)
        state = await repos.conversations.get(conversation_id)
        if state is None:
            raise SystemExit("conversation not found")
        policy = PolicyStore.from_directory(settings.lender_policy_dir).get(state.lender_id)
        ctx = ToolContext(state, policy, repos, datetime.now(UTC).date())
        forced = LLMResponse(text="[forced by scripts.live_guard_check]", tool_calls=FORCED)
        await record_tool_request(repos.events, conversation_id, forced)
        results = [(await execute(call, ctx))[0].content for call in FORCED]
        plan = await repos.plans.find_active("ACC-2002")
    finally:
        await mongo.close()
    return {
        "conversation_id": conversation_id,
        "status": state.status.value,
        "forced_results": results,
        "active_plan_for_ACC-2002": plan is not None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("conversation_id")
    report = asyncio.run(check(parser.parse_args().conversation_id))
    print(json.dumps(report, indent=2))
    (REPORTS / "session2_live_guard_check.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
