"""Build tool contexts and chat services over in-memory fakes."""

from datetime import date

from app.agent.service import ChatService
from app.agent.state import ConversationState
from app.core.settings import BACKEND_ROOT
from app.db.interfaces import Repositories
from app.llm.fake import FakeLLM
from app.policy.loader import PolicyStore
from app.tools.base import ToolContext
from tests.fakes.memory_conversations import MemoryConversations, MemoryEvents
from tests.fakes.memory_records import MemoryBorrowers, MemoryEscalations, MemoryPlans

TODAY = date(2026, 11, 5)
POLICIES = PolicyStore.from_directory(BACKEND_ROOT / "data" / "lenders")


def memory_repos() -> Repositories:
    return Repositories(
        conversations=MemoryConversations(),
        events=MemoryEvents(),
        borrowers=MemoryBorrowers(),
        plans=MemoryPlans(),
        escalations=MemoryEscalations(),
    )


async def make_ctx(
    lender_id: str = "LND-001", verified_as: str | None = None, repos: Repositories | None = None
) -> ToolContext:
    repos = repos or memory_repos()
    state = ConversationState(lender_id=lender_id, verified_borrower_id=verified_as)
    await repos.conversations.create(state)
    return ToolContext(state=state, policy=POLICIES.get(lender_id), repos=repos, today=TODAY)


def make_service(llm: FakeLLM | None = None) -> tuple[ChatService, Repositories]:
    repos = memory_repos()
    service = ChatService(llm or FakeLLM(), repos, POLICIES, today=lambda: TODAY)
    return service, repos
