"""Find payment amounts in text that already has number words turned into digits."""

import re
from decimal import Decimal

from app.extraction.date_rules import MONTHS

_NUM = r"(\d[\d,]*(?:\.\d{1,2})?)"
_DOLLAR = re.compile(rf"\$\s?{_NUM}")
_THOUSANDS = re.compile(r"\b(\d+(?:\.\d+)?)\s?k\b", re.IGNORECASE)
_NAMED = re.compile(rf"\b{_NUM}\s*(?:dollars?|bucks|usd)\b", re.IGNORECASE)
_BARE = re.compile(r"(?<![\d/$.,])\b(\d{2,4}(?:\.\d{2})?)\b(?![\d/,]|\.\d)")
# Numbers followed by these are counts, times or ordinals, not money.
_NOT_MONEY_AFTER = re.compile(
    r"\s*(?:st|nd|rd|th|days?|weeks?|months?|years?|am|pm|%|k\b)", re.IGNORECASE
)
_MONTH_BEFORE = re.compile(rf"\b(?:{'|'.join(MONTHS)})[a-z]*\.?\s*$", re.IGNORECASE)


def _decimal(raw: str) -> Decimal:
    return Decimal(raw.replace(",", ""))


def _is_bare_money(text: str, match: re.Match[str]) -> bool:
    value = _decimal(match.group(1))
    if 1900 <= value <= 2100 and "." not in match.group(1):
        return False  # a year
    after, before = text[match.end() :], text[: match.start()]
    return not _NOT_MONEY_AFTER.match(after) and not _MONTH_BEFORE.search(before)


def find_amounts(text: str) -> list[tuple[int, Decimal]]:
    """Every amount with its position, in reading order. Marked amounts win overlaps."""
    found: dict[int, tuple[int, Decimal]] = {}
    taken: list[range] = []

    def add(start: int, end: int, value: Decimal) -> None:
        if any(start in span or end - 1 in span for span in taken):
            return
        taken.append(range(start, end))
        found[start] = (start, value)

    for m in _DOLLAR.finditer(text):
        add(m.start(), m.end(), _decimal(m.group(1)))
    for m in _THOUSANDS.finditer(text):
        add(m.start(), m.end(), _decimal(m.group(1)) * 1000)
    for m in _NAMED.finditer(text):
        add(m.start(), m.end(), _decimal(m.group(1)))
    for m in _BARE.finditer(text):
        if _is_bare_money(text, m):
            add(m.start(), m.end(), _decimal(m.group(1)))
    return [found[k] for k in sorted(found)]
