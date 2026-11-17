from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.sensitivity_analysis.stock_sensitivity.basic.v1"


def solve(text: str, q: dict) -> dict:
    P = grab(r"\bP\s*=\s*{N}", text)
    c = grab(r"\bc\s*=\s*{N}\s*percent", text)
    s = grab(r"\bs\s*=\s*{N}", text)
    ratio = c / 100
    return {"final": P * ratio * s, "slots": {"market_ratio_trace": ratio}}
