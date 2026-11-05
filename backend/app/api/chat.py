"""Thin routes: send a borrower message, and read a stored conversation."""

from fastapi import APIRouter, Depends

from app.agent.results import ChatResult
from app.api.deps import ChatServiceDep, RepositoriesDep
from app.api.guards import chat_guard
from app.api.schemas import ChatRequest, ConversationView
from app.core.errors import NotFoundError

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResult, dependencies=[Depends(chat_guard)])
async def chat(body: ChatRequest, service: ChatServiceDep) -> ChatResult:
    return await service.handle(body.conversation_id, body.lender_id, body.message)


@router.get("/conversations/{conversation_id}", response_model=ConversationView)
async def get_conversation(conversation_id: str, repos: RepositoriesDep) -> ConversationView:
    state = await repos.conversations.get(conversation_id)
    if state is None:
        raise NotFoundError("Conversation not found.")
    return ConversationView.build(state, await repos.events.list(conversation_id))
