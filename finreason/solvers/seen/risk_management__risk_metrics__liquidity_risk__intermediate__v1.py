from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_metrics.liquidity_risk.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"\bV\s*=\s*{N}\s*USD", text)
    s = grab(r"spread is s\s*=\s*{N}\s*percent", text)
    ratio = s / 100
    cost = v * ratio  # additional liquidity cost = V*(s/100), unrounded
    return {"final": Fraction(cost), "slots": {"spread_ratio_trace": ratio}}
