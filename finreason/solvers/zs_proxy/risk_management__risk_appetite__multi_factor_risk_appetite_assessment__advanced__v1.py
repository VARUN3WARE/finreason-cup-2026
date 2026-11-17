from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_appetite.multi_factor_risk_appetite_assessment.advanced.v1"


def solve(text: str, q: dict) -> dict:
    c = grab(r"\bC\s*=\s*{N}", text)             # base capital, USD
    a = grab(r"\ba\s*=\s*{N}\s*percent", text)   # risk appetite, percent
    v = grab(r"\bv\s*=\s*{N}\s*percent", text)   # volatility adjustment, percent
    ratio = a / 100
    m = 1 + v / 100
    threshold = c * ratio * m
    return {"final": threshold, "slots": {"appetite_ratio_trace": ratio, "adjustment_trace": m}}
