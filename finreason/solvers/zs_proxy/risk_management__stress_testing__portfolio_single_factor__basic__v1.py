from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.stress_testing.portfolio_single_factor.basic.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"\bV\s*=\s*{N}", text)
    c = grab(r"\bc\s*=\s*{N}\s*percent", text)
    s = grab(r"\bs\s*=\s*{N}", text)
    ratio = c / 100
    return {"final": v * ratio * s, "slots": {"factor_ratio_trace": ratio}}
