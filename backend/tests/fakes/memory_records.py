"""In-memory borrower, plan and escalation repositories over the seed data."""

from datetime import date

from app.db.models import Account, Borrower
from app.db.records import Escalation, PaymentPlan
from app.db.seed_data.accounts import ACCOUNTS
from app.db.seed_data.borrowers import BORROWERS


class MemoryBorrowers:
    async def find_by_identity(self, lender_id: str, dob: date, zip_code: str) -> list[Borrower]:
        return [
            b
            for b in BORROWERS
            if (b.lender_id, b.date_of_birth, b.zip_code) == (lender_id, dob, zip_code)
        ]

    async def get_account(self, account_id: str) -> Account | None:
        return next((a for a in ACCOUNTS if a.account_id == account_id), None)

    async def list_accounts(self, borrower_id: str) -> list[Account]:
        return [a for a in ACCOUNTS if a.borrower_id == borrower_id]


class MemoryPlans:
    def __init__(self) -> None:
        self.items: list[PaymentPlan] = []

    async def find_active(self, account_id: str) -> PaymentPlan | None:
        return next((p for p in self.items if p.account_id == account_id), None)

    async def insert_once(self, plan: PaymentPlan) -> tuple[PaymentPlan, bool]:
        if existing := await self.find_active(plan.account_id):
            return existing, False
        self.items.append(plan)
        return plan, True


class MemoryEscalations:
    def __init__(self) -> None:
        self.items: dict[str, Escalation] = {}

    async def create_once(self, escalation: Escalation) -> bool:
        if escalation.conversation_id in self.items:
            return False
        self.items[escalation.conversation_id] = escalation
        return True
