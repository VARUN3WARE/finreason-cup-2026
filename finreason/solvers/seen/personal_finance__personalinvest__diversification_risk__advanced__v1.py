import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.personalinvest.diversification_risk.advanced.v1"


def solve(text: str, q: dict) -> dict:
    wa = grab(r"Asset A weight is {N}", text)
    wb = grab(r"Asset B weight is {N}", text)
    ra = grab(r"Asset A risk points are {N}", text)
    rb = grab(r"Asset B risk points are {N}", text)
    penalty = grab(r"Concentration penalty points are {N}", text)
    threshold = grab(r"larger weight is (?:at least|greater than|above|more than) {N}", text)

    # Weights used directly, no normalization.
    base = wa * ra + wb * rb
    larger = max(wa, wb)
    strict = bool(re.search(r"excluding equality|strictly", text)) and not re.search(
        r"including equality", text
    )
    applies = larger > threshold if strict else larger >= threshold
    applied = penalty if applies else Fraction(0)
    return {
        "final": base + applied,
        "slots": {
            "base_risk_score": base,
            "concentration_condition": "true" if applies else "false",
            "applied_penalty_points": applied,
        },
    }
