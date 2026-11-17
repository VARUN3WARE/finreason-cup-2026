from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.sensitivity_analysis.volatility_sensitivity.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    G = grab(r"\bG\s*=\s*{N}", text)
    n = grab(r"\bn\s*=\s*{N}", text)
    return {"final": G * n, "slots": {}}
