"""Account access shared by the tools: ownership checks and the view sent to the model."""

from typing import Any

from app.db.models import Account
from app.tools.base import ToolContext, ToolOutcome, rejected


async def owned_account(ctx: ToolContext, account_id: str) -> Account | ToolOutcome:
    """Return the account only if it belongs to the verified borrower and this lender."""
    account = await ctx.repos.borrowers.get_account(account_id)
    state = ctx.state
    if (
        account is None
        or account.borrower_id != state.verified_borrower_id
        or account.lender_id != state.lender_id
    ):
        # Same answer for "missing" and "someone else's", so nothing leaks.
        return rejected("account_not_accessible", "No account with that ID is available.")
    return account


def account_view(account: Account) -> dict[str, Any]:
    return {
        "account_id": account.account_id,
        "product": account.product,
        "balance": f"{account.balance:.2f}",
        "past_due_amount": f"{account.past_due_amount:.2f}",
        "days_past_due": account.days_past_due,
        "delinquency_stage": str(account.delinquency_stage),
        "currency": account.currency,
    }
