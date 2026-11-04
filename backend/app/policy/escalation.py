"""Deterministic escalation check run on every borrower message before the LLM.

Only clear phrases from the lender's config are matched, so false positives stay
rare. Paraphrases the phrases miss are left to the model's escalate_to_human tool.
"""

import re

from app.policy.models import EscalationReason, LenderPolicy

# Check the most protective reasons first when a message matches several.
_PRIORITY = [
    EscalationReason.STOP_CONTACT,
    EscalationReason.DISPUTE,
    EscalationReason.HARDSHIP,
    EscalationReason.HUMAN_REQUEST,
]


def normalize(text: str) -> str:
    text = text.lower().replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", text)


def detect_escalation(policy: LenderPolicy, message: str) -> EscalationReason | None:
    text = normalize(message)
    for reason in _PRIORITY:
        for phrase in policy.escalation_triggers.get(reason, []):
            if re.search(rf"(?<!\w){re.escape(normalize(phrase))}(?!\w)", text):
                return reason
    return None
