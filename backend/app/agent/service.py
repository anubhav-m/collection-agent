"""Handle one borrower message: load state, apply rules, run the loop, store it all."""

from collections.abc import Callable
from datetime import UTC, date, datetime

from app.agent.handoff import escalate_conversation, handoff_message
from app.agent.history import to_messages
from app.agent.loop import FALLBACK_MESSAGE, run_turn
from app.agent.results import ChatResult, with_handoff_notice
from app.agent.starter import load_or_start
from app.agent.state import ConversationState
from app.core.context import conversation_id_var
from app.db.interfaces import Repositories
from app.db.records import ConversationEvent, EventKind
from app.llm.interface import LLMClient
from app.policy.escalation import detect_escalation
from app.policy.loader import PolicyStore
from app.policy.models import LenderPolicy
from app.tools.base import ToolContext


def utc_today() -> date:
    return datetime.now(UTC).date()


class ChatService:
    def __init__(
        self,
        llm: LLMClient | None,
        repos: Repositories,
        policies: PolicyStore,
        today: Callable[[], date] = utc_today,
    ) -> None:
        self._llm, self._repos, self._policies, self._today = llm, repos, policies, today

    async def handle(
        self, conversation_id: str | None, lender_id: str | None, message: str
    ) -> ChatResult:
        repos = self._repos
        state = await load_or_start(repos.conversations, self._policies, conversation_id, lender_id)
        conversation_id_var.set(state.conversation_id)
        policy = self._policies.get(state.lender_id)
        await self._say(state, EventKind.USER, message)
        reply, outcome = await self._reply(state, policy, message)
        await self._say(state, EventKind.ASSISTANT, reply)
        return ChatResult.from_state(state, reply, outcome)

    async def _say(self, state: ConversationState, kind: EventKind, text: str) -> None:
        event = ConversationEvent(conversation_id=state.conversation_id, kind=kind, text=text)
        await self._repos.events.append(event)

    async def _reply(
        self, state: ConversationState, policy: LenderPolicy, message: str
    ) -> tuple[str, str]:
        # Clear-cut escalations are decided in code, before the model sees the message.
        if not state.is_escalated and (reason := detect_escalation(policy, message)):
            await escalate_conversation(self._repos, state, reason, "rule", reason.value)
            return handoff_message(state), "handoff"
        if self._llm is None:
            return FALLBACK_MESSAGE, "llm_error"
        history = to_messages(await self._repos.events.list(state.conversation_id))
        ctx = ToolContext(state=state, policy=policy, repos=self._repos, today=self._today())
        turn = await run_turn(self._llm, ctx, history)
        if state.is_escalated and turn.outcome != "handoff":
            return with_handoff_notice(turn.reply), turn.outcome
        return turn.reply, turn.outcome
