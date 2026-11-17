from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_metrics.volatility_sensitivity.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    g = grab(r"Vega is G\s*=\s*{N}\s*USD", text)
    n = grab(r"steps is n\s*=\s*{N}", text)
    return {"final": Fraction(g * n), "slots": {}}
