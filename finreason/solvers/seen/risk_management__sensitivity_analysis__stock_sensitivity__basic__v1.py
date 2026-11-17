from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.sensitivity_analysis.stock_sensitivity.basic.v1"


def solve(text: str, q: dict) -> dict:
    p = grab(r"\bP\s*=\s*{N}", text)
    c = grab(r"\bc\s*=\s*{N}", text)
    s = grab(r"\bs\s*=\s*{N}", text)
    # price change = P * (c/100) * s, signed, no intermediate rounding.
    ratio = c / 100
    change = p * ratio * s
    return {"final": change, "slots": {"market_ratio_trace": ratio}}
