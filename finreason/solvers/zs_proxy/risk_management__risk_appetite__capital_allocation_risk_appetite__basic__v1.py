from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_appetite.capital_allocation_risk_appetite.basic.v1"


def solve(text: str, q: dict) -> dict:
    c = grab(r"\bC\s*=\s*{N}", text)          # total capital, USD
    a = grab(r"\ba\s*=\s*{N}\s*percent", text)  # risk-appetite allocation, percent
    ratio = a / 100
    allocation = c * ratio
    return {"final": allocation, "slots": {"appetite_ratio_trace": ratio}}
