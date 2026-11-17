"""Liquidity cost: cost = V * (s/100); slot = spread ratio s/100."""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_metrics.liquidity_risk.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"\bV\s*=\s*{N}", text)
    s = grab(r"spread is\s+s\s*=\s*{N}\s*percent", text)
    ratio = s / Fraction(100)
    return {"final": v * ratio, "slots": {"spread_ratio_trace": ratio}}
