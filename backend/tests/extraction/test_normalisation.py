from decimal import Decimal

import pytest

from app.extraction.amounts import find_amounts
from app.extraction.number_words import replace_number_words
from app.extraction.ordinals import replace_ordinal_words


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("two hundred bucks", "200 bucks"),
        ("a hundred and fifty dollars", "150 dollars"),
        ("Three hundred and twenty-five dollars", "325 dollars"),
        ("two fifty in two weeks", "250 in 2 weeks"),
        ("one thousand two hundred", "1200"),
        ("a week from today", "a week from today"),  # "a" alone is not a number
    ],
)
def test_number_words(text, expected):
    assert replace_number_words(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [("the first", "the 1st"), ("November twentieth", "November 20th"), ("twenty-first", "21st")],
)
def test_ordinal_words(text, expected):
    assert replace_ordinal_words(text) == expected


def _values(text: str) -> list[Decimal]:
    return [v for _, v in find_amounts(text)]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("I'll pay the full $1,200 this Friday", ["1200"]),
        ("$45.50 on Monday", ["45.50"]),
        ("1.5k on December 1st", ["1500"]),
        ("I can only do 80 dollars, on the 20th", ["80"]),
        ("Not 200. I can do 120 on Monday.", ["200", "120"]),
        ("I can pay 180 on 11/20.", ["180"]),
        ("$95 by Friday, November 13?", ["95"]),
        ("I make $900 every 2 weeks", ["900"]),
        ("born March 14, 1988, ZIP 99901", []),
        ("the 5th, in 2 weeks", []),
    ],
)
def test_find_amounts(text, expected):
    assert _values(text) == [Decimal(x) for x in expected]
