"""FastAPI application factory. Run with `uvicorn app.main:app` from backend/."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.core.request_id import RequestIdMiddleware
from app.core.settings import Settings, get_settings
from app.db.indexes import ensure_indexes
from app.db.mongo import MongoDatabase

logger = logging.getLogger(__name__)


def build_mongo(settings: Settings) -> MongoDatabase:
    uri = settings.mongodb_uri.get_secret_value()
    return MongoDatabase(uri, settings.mongodb_db, settings.mongodb_timeout_ms)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    mongo = build_mongo(settings)
    app.state.mongo = mongo
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
    return app


app = create_app()
