"""Index definitions, applied idempotently at startup and before seeding."""

from pymongo import ASCENDING, IndexModel
from pymongo.asynchronous.database import AsyncDatabase

INDEXES: dict[str, list[IndexModel]] = {
    "lenders": [IndexModel([("lender_id", ASCENDING)], unique=True)],
    "borrowers": [
        IndexModel([("borrower_id", ASCENDING)], unique=True),
        IndexModel([("lender_id", ASCENDING)]),
    ],
    "accounts": [
        IndexModel([("account_id", ASCENDING)], unique=True),
        IndexModel([("borrower_id", ASCENDING)]),
        IndexModel([("lender_id", ASCENDING), ("delinquency_stage", ASCENDING)]),
    ],
    "conversations": [IndexModel([("conversation_id", ASCENDING)], unique=True)],
    "conversation_events": [IndexModel([("conversation_id", ASCENDING), ("_id", ASCENDING)])],
    "payment_plans": [
        IndexModel([("plan_id", ASCENDING)], unique=True),
        IndexModel([("idempotency_key", ASCENDING)], unique=True),
        # At most one active plan per account, even under concurrent requests.
        IndexModel(
            [("account_id", ASCENDING)],
            unique=True,
            partialFilterExpression={"status": "active"},
            name="one_active_plan_per_account",
        ),
    ],
    "escalations": [IndexModel([("conversation_id", ASCENDING)], unique=True)],
    "extractions": [
        IndexModel([("conversation_id", ASCENDING), ("extractor", ASCENDING)], unique=True)
    ],
}


async def ensure_indexes(db: AsyncDatabase) -> None:
    for collection, models in INDEXES.items():
        await db[collection].create_indexes(models)
