import pytest

from app.policy.escalation import detect_escalation
from app.policy.models import EscalationReason as R
from tests.fakes.context import POLICIES

LND1 = POLICIES.get("LND-001")


@pytest.mark.parametrize(
    ("message", "reason"),
    [
        ("This is not my debt, I never borrowed anything", R.DISPUTE),
        ("I DISPUTE this balance", R.DISPUTE),
        ("I lost my job last month", R.HARDSHIP),
        ("Please stop contacting me", R.STOP_CONTACT),
        ("Can I talk to a real person?", R.HUMAN_REQUEST),
        ("I don’t owe you this", R.DISPUTE),  # curly apostrophe from phones
    ],
)
def test_clear_phrases_escalate(message, reason):
    assert detect_escalation(LND1, message) is reason


@pytest.mark.parametrize(
    "message",
    ["What is my balance?", "Can I pay in 3 installments?", "That was undisputed, thanks"],
)
def test_ordinary_messages_do_not_escalate(message):
    assert detect_escalation(LND1, message) is None


def test_stop_contact_wins_when_several_reasons_match():
    message = "I want a supervisor and stop calling me"
    assert detect_escalation(LND1, message) is R.STOP_CONTACT
