"""Structuring detection: count condition = count >= trigger (non-strict);
amount condition = per-transaction amount < ceiling (strict); alert = both."""

import re

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.aml.structuring_detection.basic.v1"


def _op(words: str, default):
    """Map a comparison phrase to a predicate (compound phrases checked first)."""
    w = " ".join(words.lower().split())
    table = [
        ("at or above", lambda a, b: a >= b),
        ("at least", lambda a, b: a >= b),
        ("greater than or equal", lambda a, b: a >= b),
        ("no less than", lambda a, b: a >= b),
        ("at or below", lambda a, b: a <= b),
        ("at most", lambda a, b: a <= b),
        ("less than or equal", lambda a, b: a <= b),
        ("no more than", lambda a, b: a <= b),
        ("strictly above", lambda a, b: a > b),
        ("strictly greater", lambda a, b: a > b),
        ("strictly below", lambda a, b: a < b),
        ("strictly less", lambda a, b: a < b),
        ("greater than", lambda a, b: a > b),
        ("more than", lambda a, b: a > b),
        ("above", lambda a, b: a > b),
        ("less than", lambda a, b: a < b),
        ("below", lambda a, b: a < b),
    ]
    for key, fn in table:
        if key in w:
            return fn
    return default


def _tok(b: bool) -> str:
    return "true" if b else "false"


def solve(text: str, q: dict) -> dict:
    count = grab(r"Transaction count is {N}", text)
    amount = grab(r"Each transaction amount in USD is {N}", text)
    trigger = grab(r"count trigger is {N}", text)
    ceiling = grab(r"amount ceiling in USD is {N}", text)

    mc = re.search(r"count condition is true (.*?) the trigger", text, flags=re.I | re.S)
    ma = re.search(r"amount condition is true (.*?) the ceiling", text, flags=re.I | re.S)
    count_cmp = _op(mc.group(1) if mc else "", lambda a, b: a >= b)
    amt_cmp = _op(ma.group(1) if ma else "", lambda a, b: a < b)

    count_met = count_cmp(count, trigger)
    below = amt_cmp(amount, ceiling)

    m = re.search(r"Alert only when (both|either)", text, flags=re.I)
    if m is not None and m.group(1).lower() == "either":
        alert = count_met or below
    else:
        alert = count_met and below

    return {
        "final": _tok(alert),
        "slots": {
            "count_trigger_met": _tok(count_met),
            "amount_below_ceiling": _tok(below),
        },
    }
