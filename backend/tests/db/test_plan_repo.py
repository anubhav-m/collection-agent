from datetime import date
from decimal import Decimal

from pymongo.errors import DuplicateKeyError

from app.db.plans import MongoPlanRepo
from app.db.records import PaymentPlan

PLAN = PaymentPlan(
    plan_id="PLAN-1",
    idempotency_key="k1",
    conversation_id="c",
    borrower_id="BRW-002",
    account_id="ACC-1002",
    lender_id="LND-001",
    frequency="monthly",
    payments=[Decimal("850.50")],
    start_date=date(2026, 11, 12),
    total=Decimal("850.50"),
)


class RacingCollection:
    """find_one misses first, then the insert loses a race to an identical call."""

    def __init__(self) -> None:
        self.finds = 0

    async def find_one(self, query, projection):
        self.finds += 1
        return None if self.finds == 1 else PLAN.model_dump(mode="json")

    async def insert_one(self, doc):
        raise DuplicateKeyError("E11000 duplicate key")


async def test_lost_insert_race_returns_the_existing_plan():
    repo = MongoPlanRepo({"payment_plans": RacingCollection()})
    stored, created = await repo.insert_once(PLAN)
    assert created is False and stored.plan_id == "PLAN-1"
