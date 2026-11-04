"""Dependencies for the agent routes, built from objects created at startup."""

from typing import Annotated

from fastapi import Depends, Request

from app.agent.service import ChatService
from app.db.interfaces import Repositories


def get_repositories(request: Request) -> Repositories:
    return request.app.state.repos


def get_chat_service(request: Request) -> ChatService:
    state = request.app.state
    return ChatService(state.llm, state.repos, state.policies)


RepositoriesDep = Annotated[Repositories, Depends(get_repositories)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
