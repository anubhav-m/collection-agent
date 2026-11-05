"""MongoDB access for the extraction pipeline: read stored chats, save extraction results."""

from pymongo.asynchronous.database import AsyncDatabase

from app.agent.state import ConversationState
from app.extraction.stored import ExtractionRecord


class MongoConversationLister:
    def __init__(self, db: AsyncDatabase) -> None:
        self._col = db["conversations"]

    async def list_states(self) -> list[ConversationState]:
        cursor = self._col.find({}, {"_id": 0, "updated_at": 0}).sort("created_at", 1)
        return [ConversationState.model_validate(doc) async for doc in cursor]


class MongoExtractionRepo:
    def __init__(self, db: AsyncDatabase) -> None:
        self._col = db["extractions"]

    async def save(self, record: ExtractionRecord) -> None:
        """One result per conversation and extractor; a rerun replaces it."""
        key = {"conversation_id": record.conversation_id, "extractor": record.extractor}
        await self._col.replace_one(key, record.model_dump(mode="python"), upsert=True)

    async def list(self) -> list[ExtractionRecord]:
        cursor = self._col.find({}, {"_id": 0}).sort("conversation_id", 1)
        return [ExtractionRecord.model_validate(doc) async for doc in cursor]
