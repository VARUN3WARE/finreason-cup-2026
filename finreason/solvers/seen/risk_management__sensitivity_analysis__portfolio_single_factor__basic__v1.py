from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.sensitivity_analysis.portfolio_single_factor.basic.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"\bV\s*=\s*{N}", text)
    c = grab(r"\bc\s*=\s*{N}", text)
    s = grab(r"\bs\s*=\s*{N}", text)
    # change = V * (c/100) * s, signed, no intermediate rounding.
    ratio = c / 100
    change = v * ratio * s
    return {"final": change, "slots": {"factor_ratio_trace": ratio}}
