"""get_account: balances for the verified borrower's own accounts only."""

from pydantic import BaseModel, ConfigDict, Field

from app.llm.types import ToolSpec
from app.tools.accounts import account_view, owned_account
from app.tools.base import Tool, ToolContext, ToolOutcome, accepted, schema_for


class GetAccountArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str | None = Field(
        default=None, max_length=40, description="Account ID; omit to list all accounts"
    )


async def run(ctx: ToolContext, args: GetAccountArgs) -> ToolOutcome:
    if args.account_id is None:
        borrower_id = ctx.state.verified_borrower_id or ""
        accounts = await ctx.repos.borrowers.list_accounts(borrower_id)
        mine = [a for a in accounts if a.lender_id == ctx.state.lender_id]
        return accepted(accounts=[account_view(a) for a in mine])
    found = await owned_account(ctx, args.account_id)
    if isinstance(found, ToolOutcome):
        return found
    return accepted(accounts=[account_view(found)])


TOOL = Tool(
    spec=ToolSpec(
        name="get_account",
        description="Get balance and status of the verified borrower's accounts.",
        parameters=schema_for(GetAccountArgs),
    ),
    args_model=GetAccountArgs,
    run=run,
    requires_verification=True,
    allowed_after_escalation=False,
)
