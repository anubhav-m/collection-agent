"""Phrase rules that say whether a borrower turn commits, hedges, refuses or accepts."""

import re
from enum import StrEnum

# Checked in this order; the first match decides the turn.
_RETRACT = re.compile(
    r"\b(?:can'?t|cannot|won'?t|unable to|not able to|not paying|no promise|"
    r"don'?t (?:put me down|schedule)|cancel|actually no|can'?t commit)\b",
    re.I,
)
_HEDGE = re.compile(r"\b(?:if|maybe|might|perhaps|try|trying|don'?t know|hopefully)\b", re.I)
_COMMIT = re.compile(
    r"\b(?:i'?ll|i will|i can|i could|i'?m (?:sending|going to)|i am (?:sending|going to)|"
    r"let'?s do|make it|make that|i promise)\b",
    re.I,
)
_PAY_WORD = re.compile(r"\b(?:pay|paying|payment|send|sending|do)\b", re.I)
_ACCEPT = re.compile(
    r"^\s*(?:yes|yeah|yep|sure|ok|okay|deal|fine|agreed|sounds good|that works)\b", re.I
)


class TurnKind(StrEnum):
    RETRACT = "retract"
    HEDGE = "hedge"
    COMMIT = "commit"
    ACCEPT = "accept"
    ANSWER = "answer"  # gives an amount in reply to the agent's question
    OTHER = "other"


def classify(text: str, has_details: bool, after_question: bool) -> TurnKind:
    """has_details: the turn names an amount or a date. after_question: agent just asked."""
    if _RETRACT.search(text):
        return TurnKind.RETRACT
    if _HEDGE.search(text):
        return TurnKind.HEDGE
    if _COMMIT.search(text) and (has_details or _PAY_WORD.search(text)):
        return TurnKind.COMMIT
    if _ACCEPT.match(text) and after_question:
        return TurnKind.ACCEPT
    if has_details and after_question:
        return TurnKind.ANSWER
    return TurnKind.OTHER
