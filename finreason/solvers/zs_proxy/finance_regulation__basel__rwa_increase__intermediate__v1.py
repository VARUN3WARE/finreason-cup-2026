import re
from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.basel.rwa_increase.intermediate.v1"


def _meets(value: Fraction, threshold: Fraction, text: str) -> bool:
    # Stated rule: inclusive minimum threshold -> value >= threshold.
    if re.search(r"\b(?:strict|exclusive|strictly)\b", text) and not re.search(r"\binclusive\b", text):
        return value > threshold
    return value >= threshold


def solve(text: str, q: dict) -> dict:
    cap = grab(r"Total capital in USD millions (?:is|are) {N}", text)
    cur = grab(r"Current risk-weighted assets in USD millions (?:are|is) {N}", text)
    inc = grab(r"RWA increase in USD millions (?:is|are) {N}", text)
    threshold = grab(r"{N} percent threshold", text)
    new_rwa = cur + inc
    pct = cap / new_rwa * 100
    ok = _meets(pct, threshold, text)
    return {
        "final": "true" if ok else "false",
        "slots": {"new_rwa_usd_million": new_rwa, "new_capital_percent": pct},
    }
