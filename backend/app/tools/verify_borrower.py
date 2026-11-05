"""verify_borrower: match name, date of birth and ZIP against the lender's records."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.agent.handoff import escalate_conversation
from app.llm.types import ToolSpec
from app.policy.escalation import normalize
from app.policy.models import EscalationReason
from app.tools.base import Tool, ToolContext, ToolOutcome, accepted, rejected
from app.tools.schema import schema_for


class VerifyArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=1, max_length=100, description="Borrower's full name")
    date_of_birth: date = Field(description="Date of birth as YYYY-MM-DD")
    zip_code: str = Field(pattern=r"^\d{5}$", description="Five-digit ZIP code")


async def run(ctx: ToolContext, args: VerifyArgs) -> ToolOutcome:
    state, repos = ctx.state, ctx.repos
    if state.is_verified:
        return accepted(verified=True, note="Identity was already verified.")
    if state.verification_attempts_left == 0:
        return rejected("verification_locked", "No verification attempts are left.")
    candidates = await repos.borrowers.find_by_identity(
        state.lender_id, args.date_of_birth, args.zip_code
    )
    wanted = normalize(args.full_name).strip()
    match = next((b for b in candidates if normalize(b.full_name).strip() == wanted), None)
    if match:
        await repos.conversations.mark_verified(state.conversation_id, match.borrower_id)
        state.verified_borrower_id = match.borrower_id
        return accepted(verified=True)
    state.failed_verifications = await repos.conversations.add_failed_verification(
        state.conversation_id
    )
    # Never say which field was wrong, so details can't be guessed one at a time.
    outcome = rejected(
        "verification_failed",
        "The details did not match our records.",
        attempts_remaining=state.verification_attempts_left,
    )
    if state.verification_attempts_left == 0:
        await escalate_conversation(
            repos, state, EscalationReason.VERIFICATION_FAILED, "verification_limit"
        )
        outcome.escalated = True
    return outcome


TOOL = Tool(
    spec=ToolSpec(
        name="verify_borrower",
        description="Verify the borrower's identity. Required before any account detail.",
        parameters=schema_for(VerifyArgs),
    ),
    args_model=VerifyArgs,
    run=run,
    requires_verification=False,
    allowed_after_escalation=False,
)
