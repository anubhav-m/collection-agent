"""FastAPI application factory. Run with `uvicorn app.main:app` from backend/."""

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.core.handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.core.request_id import RequestIdMiddleware
from app.core.settings import Settings, get_settings
from app.db.indexes import ensure_indexes
from app.db.mongo import MongoDatabase
from app.db.repositories import mongo_repositories
from app.llm.factory import build_llm_or_none
from app.policy.loader import PolicyStore
from app.rag.startup import build_retriever

logger = logging.getLogger(__name__)


def build_mongo(settings: Settings) -> MongoDatabase:
    uri = settings.mongodb_uri.get_secret_value()
    return MongoDatabase(uri, settings.mongodb_db, settings.mongodb_timeout_ms)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    mongo = build_mongo(settings)
    app.state.mongo = mongo
    app.state.repos = mongo_repositories(mongo.db)
    app.state.policies = PolicyStore.from_directory(settings.lender_policy_dir)
    app.state.llm = build_llm_or_none(settings)
    # Loading the ONNX model and checking the store is blocking work; run it off the loop.
    app.state.retriever = await asyncio.to_thread(build_retriever, settings, app.state.policies)
    if await mongo.ping():
        await ensure_indexes(mongo.db)
        logger.info("startup complete", extra={"database": "connected"})
    else:
        # Start anyway so /health can report the outage instead of crashing.
        logger.warning("startup without database", extra={"database": "disconnected"})
    try:
        yield
    finally:
        await mongo.close()
        logger.info("shutdown complete")


def create_app() -> FastAPI:
    configure_logging(get_settings().log_level)
    app = FastAPI(title="Collections AI Agent (simulation)", lifespan=lifespan)
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(chat_router)
    return app


app = create_app()
