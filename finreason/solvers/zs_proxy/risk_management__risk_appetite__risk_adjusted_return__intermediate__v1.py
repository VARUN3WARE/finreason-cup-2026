from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_appetite.risk_adjusted_return.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    c = grab(r"\bC\s*=\s*{N}", text)             # capital, USD
    f = grab(r"\bf\s*=\s*{N}\s*percent", text)   # risk factor, percent
    p = grab(r"\bp\s*=\s*{N}\s*percent", text)   # risk premium, percent
    fr = f / 100
    pr = p / 100
    extra = c * fr * pr
    return {"final": extra, "slots": {"factor_ratio_trace": fr, "premium_ratio_trace": pr}}
