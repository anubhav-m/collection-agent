"""create_payment_plan: save a plan only if the lender's rules allow it. Idempotent."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.db.records import PaymentPlan
from app.llm.types import ToolSpec
from app.policy.models import Frequency, PlanTerms
from app.policy.rules import plan_violations, to_money
from app.tools.accounts import owned_account
from app.tools.base import Tool, ToolContext, ToolOutcome, accepted, rejected
from app.tools.plan_identity import plan_key, plan_view
from app.tools.schema import schema_for


class CreatePlanArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str = Field(max_length=40, description="Account ID")
    frequency: Frequency
    payments: list[Decimal] = Field(min_length=1, max_length=60, description="Each amount")
    start_date: date = Field(description="First payment date, YYYY-MM-DD")


async def run(ctx: ToolContext, args: CreatePlanArgs) -> ToolOutcome:
    found = await owned_account(ctx, args.account_id)
    if isinstance(found, ToolOutcome):
        return found
    balance = to_money(found.balance)
    terms = PlanTerms(frequency=args.frequency, payments=args.payments, start_date=args.start_date)
    if problems := plan_violations(ctx.policy, balance, terms, ctx.today):
        return rejected(
            "plan_not_allowed", "The plan breaks the lender's rules.", problems=problems
        )
    key = plan_key(ctx.state.conversation_id, found.account_id, terms)
    plan = PaymentPlan(
        plan_id=f"PLAN-{key[:16]}",
        idempotency_key=key,
        conversation_id=ctx.state.conversation_id,
        borrower_id=found.borrower_id,
        account_id=found.account_id,
        lender_id=found.lender_id,
        frequency=terms.frequency,
        payments=[to_money(p) for p in terms.payments],
        start_date=terms.start_date,
        total=balance,
    )
    stored, created = await ctx.repos.plans.insert_once(plan)
    if not created and stored.idempotency_key != key:
        return rejected(
            "plan_already_exists",
            "This account already has an active plan.",
            existing_plan=plan_view(stored),
        )
    return accepted(plan=plan_view(stored), already_saved=not created)


TOOL = Tool(
    spec=ToolSpec(
        name="create_payment_plan",
        description="Save a payment plan the borrower agreed to. Payments must sum to balance.",
        parameters=schema_for(CreatePlanArgs),
    ),
    args_model=CreatePlanArgs,
    run=run,
    requires_verification=True,
    allowed_after_escalation=False,
)
