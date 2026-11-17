"""Vega sensitivity: change = G*n (signed)."""
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_metrics.volatility_sensitivity.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    g = grab(r"\bG\s*=\s*{N}", text)
    n = grab(r"\bn\s*=\s*{N}", text)
    return {"final": g * n, "slots": {}}
