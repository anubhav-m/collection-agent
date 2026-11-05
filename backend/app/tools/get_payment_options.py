"""get_payment_options: the plans the lender's rules allow for one account."""

from datetime import timedelta

from pydantic import BaseModel, ConfigDict, Field

from app.llm.types import ToolSpec
from app.policy.rules import payment_options, to_money
from app.tools.accounts import owned_account
from app.tools.base import Tool, ToolContext, ToolOutcome, accepted
from app.tools.schema import schema_for


class PaymentOptionsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str = Field(max_length=40, description="Account ID")


async def run(ctx: ToolContext, args: PaymentOptionsArgs) -> ToolOutcome:
    found = await owned_account(ctx, args.account_id)
    if isinstance(found, ToolOutcome):
        return found
    balance = to_money(found.balance)
    policy = ctx.policy
    options = [
        {"installments": o.installments, "payments": [f"{p:.2f}" for p in o.payments]}
        for o in payment_options(policy, balance)
    ]
    latest = ctx.today + timedelta(days=policy.max_days_to_first_payment)
    return accepted(
        account_id=found.account_id,
        balance=f"{balance:.2f}",
        options=options,
        allowed_frequencies=[f.value for f in policy.allowed_frequencies],
        first_payment_between=[ctx.today.isoformat(), latest.isoformat()],
    )


TOOL = Tool(
    spec=ToolSpec(
        name="get_payment_options",
        description="List payment plans the lender allows for an account.",
        parameters=schema_for(PaymentOptionsArgs),
    ),
    args_model=PaymentOptionsArgs,
    run=run,
    requires_verification=True,
    allowed_after_escalation=False,
)
