"""escalate_to_human: hand the conversation to a person. Allowed at any point."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.agent.handoff import escalate_conversation
from app.llm.types import ToolSpec
from app.policy.models import EscalationReason
from app.tools.base import Tool, ToolContext, ToolOutcome, accepted, schema_for


class ModelReason(StrEnum):
    """The reasons the model may give; verification_failed is set only by the server."""

    DISPUTE = "dispute"
    HARDSHIP = "hardship"
    STOP_CONTACT = "stop_contact"
    HUMAN_REQUEST = "human_request"
    OTHER = "other"


class EscalateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: ModelReason
    summary: str = Field(default="", max_length=300, description="One-line reason")


async def run(ctx: ToolContext, args: EscalateArgs) -> ToolOutcome:
    reason = EscalationReason(args.reason.value)
    changed = await escalate_conversation(ctx.repos, ctx.state, reason, "model", args.summary)
    outcome = accepted(escalated=True, already_escalated=not changed)
    outcome.escalated = True
    return outcome


TOOL = Tool(
    spec=ToolSpec(
        name="escalate_to_human",
        description=(
            "Hand off to a person for a dispute, hardship, stop-contact request, "
            "or a request for a person."
        ),
        parameters=schema_for(EscalateArgs),
    ),
    args_model=EscalateArgs,
    run=run,
    requires_verification=False,
    allowed_after_escalation=True,
)
