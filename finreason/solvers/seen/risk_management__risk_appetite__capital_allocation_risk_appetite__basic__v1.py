from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_appetite.capital_allocation_risk_appetite.basic.v1"


def solve(text: str, q: dict) -> dict:
    capital = grab(r"Total capital is C\s*=\s*{N}", text)
    a_pct = grab(r"allocation is a\s*=\s*{N}\s*percent", text)
    ratio = a_pct / 100
    allocation = capital * ratio
    return {"final": allocation, "slots": {"appetite_ratio_trace": ratio}}
