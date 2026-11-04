"""MongoDB storage for payment plans and escalations, both written at most once."""

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

from app.db.records import Escalation, PaymentPlan

_ACTIVE = "active"


class MongoPlanRepo:
    def __init__(self, db: AsyncDatabase) -> None:
        self._col = db["payment_plans"]

    async def find_active(self, account_id: str) -> PaymentPlan | None:
        doc = await self._col.find_one({"account_id": account_id, "status": _ACTIVE}, {"_id": 0})
        return PaymentPlan.model_validate(doc) if doc else None

    async def insert_once(self, plan: PaymentPlan) -> tuple[PaymentPlan, bool]:
        if existing := await self.find_active(plan.account_id):
            return existing, False
        try:
            await self._col.insert_one(
                plan.model_dump(mode="json") | {"created_at": plan.created_at}
            )
        except DuplicateKeyError:
            # A concurrent identical call won the race; the unique index kept one copy.
            existing = await self.find_active(plan.account_id)
            if existing is None:
                raise
            return existing, False
        return plan, True


class MongoEscalationRepo:
    def __init__(self, db: AsyncDatabase) -> None:
        self._col = db["escalations"]

    async def create_once(self, escalation: Escalation) -> bool:
        doc = escalation.model_dump(mode="json") | {"created_at": escalation.created_at}
        result = await self._col.update_one(
            {"conversation_id": escalation.conversation_id},
            {"$setOnInsert": doc},
            upsert=True,
        )
        return result.upserted_id is not None
