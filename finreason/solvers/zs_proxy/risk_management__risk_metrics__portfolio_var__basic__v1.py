"""Parametric VaR with supplied multiplier: VaR = V*(s/100)*z; slot = s/100."""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_metrics.portfolio_var.basic.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"\bV\s*=\s*{N}", text)
    s = grab(r"volatility is\s+s\s*=\s*{N}\s*percent", text)
    z = grab(r"\bz\s*=\s*{N}", text)
    ratio = s / Fraction(100)
    return {"final": v * ratio * z, "slots": {"volatility_ratio_trace": ratio}}
