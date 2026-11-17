"""Multi-entity ownership: aggregate = sum of entity percents, largest = max;
review = (aggregate >= aggregate threshold) OR (largest >= single-entity threshold)."""

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "fp.finance_regulation.aml.multi_entity_ownership.intermediate.v1"


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


def _tok(b: bool) -> str:
    return "true" if b else "false"


def solve(text: str, q: dict) -> dict:
    vals = [F(v) for v in re.findall(r"Entity \w+ ownership percent is (" + NUMBER + r")", text)]
    if not vals:
        raise ValueError("no entity ownership percents found")
    agg_thr = grab(r"aggregate threshold percent is {N}", text)
    single_thr = grab(r"single-entity threshold percent is {N}", text)

    aggregate = sum(vals, Fraction(0))
    largest = max(vals)

    m1 = re.search(r"the aggregate is (.*?) its threshold", text, flags=re.I | re.S)
    m2 = re.search(r"the maximum is (.*?) its threshold", text, flags=re.I | re.S)
    agg_hit = (_op(m1.group(1)) if m1 else _op("at least"))(aggregate, agg_thr)
    max_hit = (_op(m2.group(1)) if m2 else _op("at least"))(largest, single_thr)

    mj = re.search(r"its threshold (or|and) the maximum", text, flags=re.I)
    if mj is not None and mj.group(1).lower() == "and":
        review = agg_hit and max_hit
    else:
        review = agg_hit or max_hit

    return {
        "final": _tok(review),
        "slots": {
            "aggregate_ownership_percent": aggregate,
            "largest_entity_percent": largest,
        },
    }
