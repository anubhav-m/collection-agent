"""Small builders for extraction tests."""

from datetime import date

from app.extraction.models import Speaker, Transcript, Turn


def chat(*turns: str, ref: date = date(2026, 11, 4), tid: str = "t1") -> Transcript:
    """Turns alternate by prefix: 'A: ...' is the agent, 'B: ...' the borrower."""
    parsed = [
        Turn(speaker=Speaker.AGENT if t.startswith("A:") else Speaker.BORROWER, text=t[2:].strip())
        for t in turns
    ]
    return Transcript(id=tid, reference_date=ref, turns=parsed)


class Lister:
    def __init__(self, states):
        self.states = states

    async def list_states(self):
        return self.states


class Sink:
    def __init__(self):
        self.saved = []

    async def save(self, record):
        self.saved.append(record)
