"""Beneficial ownership: total = direct + indirect; review = (total >= threshold) OR control flag."""

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.aml.beneficial_ownership.intermediate.v1"


def _op(words: str):
    """Map a comparison phrase to a predicate (compound phrases checked first)."""
    w = " ".join(words.lower().split())
    table = [
        ("at least", lambda a, b: a >= b),
        ("at or above", lambda a, b: a >= b),
        ("greater than or equal", lambda a, b: a >= b),
        ("no less than", lambda a, b: a >= b),
        ("at most", lambda a, b: a <= b),
        ("at or below", lambda a, b: a <= b),
        ("less than or equal", lambda a, b: a <= b),
        ("no more than", lambda a, b: a <= b),
        ("strictly above", lambda a, b: a > b),
        ("strictly greater", lambda a, b: a > b),
        ("strictly below", lambda a, b: a < b),
        ("strictly less", lambda a, b: a < b),
        ("greater than", lambda a, b: a > b),
        ("more than", lambda a, b: a > b),
        ("exceed", lambda a, b: a > b),
        ("above", lambda a, b: a > b),
        ("less than", lambda a, b: a < b),
        ("below", lambda a, b: a < b),
    ]
    for key, fn in table:
        if key in w:
            return fn
    return lambda a, b: a >= b  # template default: "at least"


def _flag(name: str, text: str) -> bool:
    m = re.search(name + r"\s+is\s+(true|false)", text, flags=re.I)
    if m is None:
        raise ValueError(f"flag not found: {name}")
    return m.group(1).lower() == "true"


def _tok(b: bool) -> str:
    return "true" if b else "false"


def solve(text: str, q: dict) -> dict:
    direct = grab(r"Direct ownership percent is {N}", text)
    indirect = grab(r"Indirect ownership percent is {N}", text)
    threshold = grab(r"ownership threshold percent is {N}", text)
    control = _flag(r"control flag", text)

    total = direct + indirect

    m = re.search(r"total ownership is (.*?) the threshold", text, flags=re.I | re.S)
    cmp = _op(m.group(1)) if m else _op("at least")
    met = cmp(total, threshold)

    # Combination of the ownership condition and the control flag ("or" by default).
    m2 = re.search(r"the threshold (or|and) the control flag", text, flags=re.I)
    if m2 is not None and m2.group(1).lower() == "and":
        review = met and control
    else:
        review = met or control

    return {
        "final": _tok(review),
        "slots": {
            "total_ownership_percent": Fraction(total),
            "ownership_threshold_met": _tok(met),
        },
    }
