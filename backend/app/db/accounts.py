"""Read-only MongoDB access to seeded borrowers and accounts."""

from datetime import date

from pymongo.asynchronous.database import AsyncDatabase

from app.db.models import Account, Borrower

_HIDE = {"_id": 0, "created_at": 0, "updated_at": 0}


class MongoBorrowerRepo:
    def __init__(self, db: AsyncDatabase) -> None:
        self._borrowers = db["borrowers"]
        self._accounts = db["accounts"]

    async def find_by_identity(
        self, lender_id: str, date_of_birth: date, zip_code: str
    ) -> list[Borrower]:
        query = {
            "lender_id": lender_id,
            "date_of_birth": date_of_birth.isoformat(),
            "zip_code": zip_code,
        }
        return [Borrower.model_validate(d) async for d in self._borrowers.find(query, _HIDE)]

    async def get_account(self, account_id: str) -> Account | None:
        doc = await self._accounts.find_one({"account_id": account_id}, _HIDE)
        return Account.model_validate(doc) if doc else None

    async def list_accounts(self, borrower_id: str) -> list[Account]:
        cursor = self._accounts.find({"borrower_id": borrower_id}, _HIDE).sort("account_id", 1)
        return [Account.model_validate(d) async for d in cursor]
