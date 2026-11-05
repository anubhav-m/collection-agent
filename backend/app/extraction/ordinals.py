"""Turn ordinal words into digits: "the first" -> "the 1st", "twenty-first" -> "21st"."""

import re

_UNITS = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth"]
_TEENS = [
    "tenth",
    "eleventh",
    "twelfth",
    "thirteenth",
    "fourteenth",
    "fifteenth",
    "sixteenth",
    "seventeenth",
    "eighteenth",
    "nineteenth",
]
_SUFFIX = {1: "st", 2: "nd", 3: "rd", 21: "st", 22: "nd", 23: "rd", 31: "st"}

ORDINALS: dict[str, int] = {w: i + 1 for i, w in enumerate(_UNITS)}
ORDINALS |= {w: i + 10 for i, w in enumerate(_TEENS)}
ORDINALS |= {"twentieth": 20, "thirtieth": 30}
ORDINALS |= {f"twenty-{w}": 21 + i for i, w in enumerate(_UNITS)}
ORDINALS |= {f"twenty {w}": 21 + i for i, w in enumerate(_UNITS)}
ORDINALS |= {"thirty-first": 31, "thirty first": 31}

# Longest first, so "twenty-first" is replaced before "first".
_PATTERN = re.compile(
    r"\b(" + "|".join(sorted(ORDINALS, key=len, reverse=True)) + r")\b", re.IGNORECASE
)


def as_ordinal(day: int) -> str:
    return f"{day}{_SUFFIX.get(day, 'th')}"


def replace_ordinal_words(text: str) -> str:
    return _PATTERN.sub(lambda m: as_ordinal(ORDINALS[m.group(1).lower()]), text)
