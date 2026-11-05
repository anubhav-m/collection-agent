"""The one interface both extractors implement, so the benchmark and pipeline can swap them."""

from typing import Protocol

from app.extraction.models import ExtractionOutcome, Transcript


class Extractor(Protocol):
    name: str

    async def extract(self, transcript: Transcript) -> ExtractionOutcome:
        """Never raises for a bad transcript or model reply; failures go in outcome.error."""
        ...
