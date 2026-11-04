"""Async MongoDB connection wrapper used by the app and scripts."""

import logging

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


class MongoDatabase:
    def __init__(self, uri: str, db_name: str, timeout_ms: int = 5000) -> None:
        self._client: AsyncMongoClient = AsyncMongoClient(
            uri,
            serverSelectionTimeoutMS=timeout_ms,
            connectTimeoutMS=timeout_ms,
            socketTimeoutMS=timeout_ms * 4,
            tz_aware=True,
            appname="collections-agent",
        )
        self.db: AsyncDatabase = self._client[db_name]

    async def ping(self) -> bool:
        try:
            await self._client.admin.command("ping")
        except PyMongoError as exc:
            # Exception text can include the host; log only the type.
            logger.warning("mongodb ping failed", extra={"exc_type": type(exc).__name__})
            return False
        return True

    async def close(self) -> None:
        await self._client.close()
