"""Idempotent seed command: `python -m app.db.seed` (run from backend/)."""

import asyncio
import json
import logging
from datetime import UTC, datetime

from pymongo.asynchronous.database import AsyncDatabase

from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.db.indexes import ensure_indexes
from app.db.mongo import MongoDatabase
from app.db.seed_data.accounts import ACCOUNTS
from app.db.seed_data.borrowers import BORROWERS
from app.db.seed_data.lenders import LENDERS

logger = logging.getLogger(__name__)

# collection -> (natural key field, records)
SEED_PLAN = {
    "lenders": ("lender_id", LENDERS),
    "borrowers": ("borrower_id", BORROWERS),
    "accounts": ("account_id", ACCOUNTS),
}


async def seed(db: AsyncDatabase) -> dict[str, dict[str, int]]:
    """Upsert every record by its natural key, so reruns never duplicate."""
    await ensure_indexes(db)
    summary: dict[str, dict[str, int]] = {}
    now = datetime.now(UTC)
    for name, (key, records) in SEED_PLAN.items():
        inserted = 0
        for record in records:
            doc = record.model_dump(mode="json")
            result = await db[name].update_one(
                {key: doc[key]},
                {"$set": doc | {"updated_at": now}, "$setOnInsert": {"created_at": now}},
                upsert=True,
            )
            inserted += 1 if result.upserted_id is not None else 0
        total = await db[name].count_documents({})
        summary[name] = {"inserted": inserted, "total": total}
    return summary


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    mongo = MongoDatabase(
        settings.mongodb_uri.get_secret_value(), settings.mongodb_db, settings.mongodb_timeout_ms
    )
    try:
        summary = await seed(mongo.db)
    finally:
        await mongo.close()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
