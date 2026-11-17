import re
from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.basel.leverage_ratio.basic.v1"


def _meets(value: Fraction, threshold: Fraction, text: str) -> bool:
    # Default (and stated) rule: inclusive minimum threshold -> value >= threshold.
    if re.search(r"\b(?:strict|exclusive|strictly)\b", text) and not re.search(r"\binclusive\b", text):
        return value > threshold
    return value >= threshold


def solve(text: str, q: dict) -> dict:
    t1 = grab(r"Tier 1 capital in USD millions (?:is|are) {N}", text)
    exposure = grab(r"Exposure in USD millions (?:is|are) {N}", text)
    threshold = grab(r"{N} percent threshold", text)
    lev_pct = t1 / exposure * 100
    ok = _meets(lev_pct, threshold, text)
    return {"final": "true" if ok else "false", "slots": {"leverage_percent": lev_pct}}
