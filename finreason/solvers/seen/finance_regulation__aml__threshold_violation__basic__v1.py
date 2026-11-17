"""Threshold violation: signed excess = amount - threshold; breach = amount >= threshold
(equality breaches)."""

import re

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.aml.threshold_violation.basic.v1"


def _op(words: str, default):
    """Map a comparison phrase to a predicate (compound phrases checked first)."""
    w = " ".join(words.lower().split())
    table = [
        ("at least", lambda a, b: a >= b),
        ("at or above", lambda a, b: a >= b),
        ("greater than or equal", lambda a, b: a >= b),
        ("no less than", lambda a, b: a >= b),
        ("strictly above", lambda a, b: a > b),
        ("strictly greater", lambda a, b: a > b),
        ("greater than", lambda a, b: a > b),
        ("more than", lambda a, b: a > b),
        ("exceed", lambda a, b: a > b),
        ("above", lambda a, b: a > b),
    ]
    for key, fn in table:
        if key in w:
            return fn
    return default


def solve(text: str, q: dict) -> dict:
    amount = grab(r"transaction amount in USD is {N}", text)
    threshold = grab(r"scenario threshold in USD is {N}", text)

    excess = amount - threshold

    m = re.search(r"breach is true exactly when amount is (.*?) the threshold", text, flags=re.I | re.S)
    cmp = _op(m.group(1) if m else "", lambda a, b: a >= b)
    breach = cmp(amount, threshold)

    return {
        "final": "true" if breach else "false",
        "slots": {"amount_excess": excess},
    }
