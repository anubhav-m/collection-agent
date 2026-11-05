"""Play one scenario's turns through the real chat service and collect its trace."""

import time
from collections.abc import Callable
from datetime import date

from app.agent.service import ChatService
from app.db.interfaces import Repositories
from app.evaluation.recorder import RecordingLLM
from app.evaluation.scenarios import Scenario
from app.evaluation.trace import ScenarioTrace, TurnTrace
from app.evaluation.trace_build import build_trace
from app.policy.loader import PolicyStore
from app.rag.retriever import PolicyRetriever


async def run_scenario(
    scenario: Scenario,
    repos: Repositories,
    llm: RecordingLLM,
    policies: PolicyStore,
    retriever: PolicyRetriever | None,
    today: Callable[[], date],
) -> ScenarioTrace:
    llm.reset()
    service = ChatService(llm, repos, policies, today, retriever)
    turns: list[TurnTrace] = []
    conversation_id: str | None = None
    for message in scenario.turns:
        lender = scenario.lender_id if conversation_id is None else None
        started = time.perf_counter()
        result = await service.handle(conversation_id, lender, message)
        conversation_id = result.conversation_id
        turns.append(
            TurnTrace(
                message=message,
                reply=result.reply,
                outcome=result.outcome,
                latency_ms=round((time.perf_counter() - started) * 1000, 1),
                verified=result.verified,
                sources=[s.doc_id for s in result.sources],
            )
        )
    assert conversation_id is not None  # scenarios have at least one turn
    return await build_trace(repos, conversation_id, turns, llm)
