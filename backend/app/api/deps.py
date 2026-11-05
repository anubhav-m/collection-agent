"""Dependencies for the agent routes, built from objects created at startup."""

from typing import Annotated

from fastapi import Depends, Request

from app.agent.service import ChatService
from app.db.interfaces import Repositories
from app.llm.budget import BudgetedLLM


def get_repositories(request: Request) -> Repositories:
    return request.app.state.repos


def get_chat_service(request: Request) -> ChatService:
    state = request.app.state
    llm = BudgetedLLM(state.llm, state.llm_budget) if state.llm is not None else None
    return ChatService(llm, state.repos, state.policies, retriever=state.retriever)


RepositoriesDep = Annotated[Repositories, Depends(get_repositories)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
