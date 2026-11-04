"""Every tool the agent may request, keyed by name."""

from app.llm.types import ToolSpec
from app.tools import (
    create_payment_plan,
    escalate_to_human,
    get_account,
    get_payment_options,
    verify_borrower,
)
from app.tools.base import Tool

TOOLS: dict[str, Tool] = {
    module.TOOL.spec.name: module.TOOL
    for module in (
        verify_borrower,
        get_account,
        get_payment_options,
        create_payment_plan,
        escalate_to_human,
    )
}


def tool_specs() -> list[ToolSpec]:
    return [tool.spec for tool in TOOLS.values()]
