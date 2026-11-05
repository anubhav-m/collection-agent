"""Read everything the reporting load needs from MongoDB in one pass."""

from dataclasses import dataclass
from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.agent.state import ConversationState
from app.db.extractions import MongoConversationLister
from app.extraction.stored import ExtractionRecord

_HIDE = {"_id": 0}


@dataclass
class ProjectSnapshot:
    lenders: list[dict[str, Any]]
    borrowers: list[dict[str, Any]]
    conversations: list[ConversationState]
    escalations: list[dict[str, Any]]
    extractions: list[ExtractionRecord]


async def _all(db: AsyncDatabase, name: str, projection: dict[str, int]) -> list[dict]:
    return [doc async for doc in db[name].find({}, projection)]


async def read_project_snapshot(db: AsyncDatabase, extractor: str) -> ProjectSnapshot:
    # Only ids are copied for borrowers: reports never need names or dates of birth.
    found = db["extractions"].find({"extractor": extractor}, _HIDE)
    return ProjectSnapshot(
        lenders=await _all(db, "lenders", {"_id": 0, "lender_id": 1, "name": 1}),
        borrowers=await _all(db, "borrowers", {"_id": 0, "borrower_id": 1, "lender_id": 1}),
        conversations=await MongoConversationLister(db).list_states(),
        escalations=await _all(db, "escalations", _HIDE),
        extractions=[ExtractionRecord.model_validate(doc) async for doc in found],
    )
