"""Find every payment date in a piece of text, resolved against a fixed reference date."""

from datetime import date

from app.extraction.date_rules import RULES

Found = tuple[int, int, int, date]  # priority, start, end, date


def _inside_another(item: Found, found: list[Found]) -> bool:
    # "today" inside "a week from today" is part of the longer phrase, not its own date.
    _, start, end, _ = item
    return any(o[1] <= start and end <= o[2] and (o[1], o[2]) != (start, end) for o in found)


def find_dates(text: str, ref: date) -> list[tuple[int, int, date]]:
    """(priority, position, date) for every date found, in no particular order."""
    found: list[Found] = []
    for priority, pattern, resolve in RULES:
        for m in pattern.finditer(text):
            if (when := resolve(m, ref)) is not None:
                found.append((priority, m.start(), m.end(), when))
    return [(p, s, d) for p, s, e, d in found if not _inside_another((p, s, e, d), found)]
