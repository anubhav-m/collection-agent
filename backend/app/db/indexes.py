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
}


async def ensure_indexes(db: AsyncDatabase) -> None:
    for collection, models in INDEXES.items():
        await db[collection].create_indexes(models)
