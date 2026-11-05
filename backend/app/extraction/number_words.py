"""Turn spelled-out numbers into digits: "a hundred and fifty" -> 150, "two fifty" -> 250."""

import re

_ONES = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
_TEENS = [
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
]
_TENS = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
VALUES = {w: i + 1 for i, w in enumerate(_ONES)}
VALUES |= {w: i + 10 for i, w in enumerate(_TEENS)}
VALUES |= {w: (i + 2) * 10 for i, w in enumerate(_TENS)}
_SCALES = {"hundred": 100, "thousand": 1000}

_WORD = "|".join([*VALUES, *_SCALES])
# "a" counts only right before a scale word ("a hundred"); "and" only between number words.
_RUN = re.compile(
    rf"\b(?:a[\s-]+(?=hundred|thousand))?(?:{_WORD})\b(?:(?:[\s-]+(?:and[\s-]+)?)(?:{_WORD})\b)*",
    re.IGNORECASE,
)


def words_to_int(words: list[str]) -> int:
    total, current, previous = 0, 0, ""
    for word in words:
        if word in _SCALES:
            current = (current or 1) * _SCALES[word]
            if word == "thousand":
                total, current = total + current, 0
        elif previous in _ONES and VALUES[word] >= 10:
            current = current * 100 + VALUES[word]  # "two fifty": spoken hundreds
        else:
            current += VALUES[word]
        previous = word
    return total + current


def replace_number_words(text: str) -> str:
    def convert(match: re.Match[str]) -> str:
        words = [w for w in re.split(r"[\s-]+", match.group(0).lower()) if w not in ("a", "and")]
        return str(words_to_int(words))

    return _RUN.sub(convert, text)
