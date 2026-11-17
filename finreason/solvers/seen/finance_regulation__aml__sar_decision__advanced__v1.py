"""SAR decision ladder.
high_trigger   = score >= high threshold OR (transaction flag AND identity flag)
review_trigger = score >= medium threshold OR (transaction flag OR identity flag)
final = file_sar if high_trigger (precedence) else manual_review if review_trigger else no_action."""

import re

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.aml.sar_decision.advanced.v1"


def _op(words: str):
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
    return lambda a, b: a >= b  # template default: "at least"


def _flag(name: str, text: str) -> bool:
    m = re.search(name + r"\s+is\s+(true|false)", text, flags=re.I)
    if m is None:
        raise ValueError(f"flag not found: {name}")
    return m.group(1).lower() == "true"


def _tok(b: bool) -> str:
    return "true" if b else "false"


def solve(text: str, q: dict) -> dict:
    score = grab(r"Base risk score is {N}", text)
    tx = _flag(r"Transaction flag", text)
    ident = _flag(r"Identity flag", text)
    medium = grab(r"medium score threshold is {N}", text)
    high = grab(r"high score threshold is {N}", text)

    mh = re.search(r"Return file_sar when score is (.*?)\s*-?\d", text, flags=re.I | re.S)
    mm = re.search(r"return manual_review when score is (.*?)\s*-?\d", text, flags=re.I | re.S)
    high_cmp = _op(mh.group(1)) if mh else _op("at least")
    med_cmp = _op(mm.group(1)) if mm else _op("at least")

    high_trigger = high_cmp(score, high) or (tx and ident)
    review_trigger = med_cmp(score, medium) or (tx or ident)

    if high_trigger:
        label = "file_sar"
    elif review_trigger:
        label = "manual_review"
    else:
        label = "no_action"

    return {
        "final": label,
        "slots": {
            "high_trigger": _tok(high_trigger),
            "review_trigger": _tok(review_trigger),
        },
    }
