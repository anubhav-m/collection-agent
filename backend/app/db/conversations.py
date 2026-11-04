"""MongoDB storage for conversation state and its event log."""

from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.agent.state import ConversationState, ConversationStatus
from app.db.records import ConversationEvent, utc_now
from app.policy.models import EscalationReason


class MongoConversationRepo:
    def __init__(self, db: AsyncDatabase) -> None:
        self._col = db["conversations"]

    async def create(self, state: ConversationState) -> None:
        await self._col.insert_one(state.model_dump(mode="python") | {"updated_at": utc_now()})

    async def get(self, conversation_id: str) -> ConversationState | None:
        doc = await self._col.find_one({"conversation_id": conversation_id}, {"_id": 0})
        return ConversationState.model_validate(doc) if doc else None

    async def mark_verified(self, conversation_id: str, borrower_id: str) -> None:
        await self._col.update_one(
            {"conversation_id": conversation_id},
            {"$set": {"verified_borrower_id": borrower_id, "updated_at": utc_now()}},
        )

    async def add_failed_verification(self, conversation_id: str) -> int:
        doc = await self._col.find_one_and_update(
            {"conversation_id": conversation_id},
            {"$inc": {"failed_verifications": 1}, "$set": {"updated_at": utc_now()}},
            return_document=ReturnDocument.AFTER,
        )
        return int(doc["failed_verifications"]) if doc else 0

    async def escalate(self, conversation_id: str, reason: EscalationReason) -> bool:
        # Filtering on ACTIVE makes the first escalation win and repeats a no-op.
        result = await self._col.update_one(
            {"conversation_id": conversation_id, "status": ConversationStatus.ACTIVE.value},
            {
                "$set": {
                    "status": ConversationStatus.ESCALATED.value,
                    "escalation_reason": reason.value,
                    "updated_at": utc_now(),
                }
            },
        )
        return result.modified_count == 1


class MongoEventRepo:
    def __init__(self, db: AsyncDatabase) -> None:
        self._col = db["conversation_events"]

    async def append(self, event: ConversationEvent) -> None:
        await self._col.insert_one(event.model_dump(mode="python"))

    async def list(self, conversation_id: str) -> list[ConversationEvent]:
        # ObjectIds from one process increase, so _id order is insertion order.
        cursor = self._col.find({"conversation_id": conversation_id}, {"_id": 0}).sort("_id", 1)
        return [ConversationEvent.model_validate(doc) async for doc in cursor]
