"""What one scenario run produced: replies, tool trace, database state and LLM usage."""

from pydantic import BaseModel


class TurnTrace(BaseModel):
    message: str
    reply: str
    outcome: str
    latency_ms: float
    verified: bool  # server state after this turn
    sources: list[str] = []  # doc_ids retrieved during this turn


class ToolResultTrace(BaseModel):
    name: str
    accepted: bool
    reason: str | None = None


class PlanTrace(BaseModel):
    account_id: str
    installments: int
    frequency: str


class LLMUsage(BaseModel):
    calls: int = 0
    prompt_tokens: int = 0
    output_tokens: int = 0
    thinking_tokens: int = 0
    total_tokens: int = 0
    call_latencies_ms: list[float] = []


class ScenarioTrace(BaseModel):
    conversation_id: str
    turns: list[TurnTrace]
    tool_requests: list[str]
    tool_results: list[ToolResultTrace]
    verified_borrower_id: str | None
    escalated: bool
    escalation_reason: str | None
    failed_verifications: int
    plans: list[PlanTrace]
    usage: LLMUsage

    def accepted_tools(self) -> set[str]:
        return {r.name for r in self.tool_results if r.accepted}

    def all_sources(self) -> set[str]:
        return {doc for turn in self.turns for doc in turn.sources}
