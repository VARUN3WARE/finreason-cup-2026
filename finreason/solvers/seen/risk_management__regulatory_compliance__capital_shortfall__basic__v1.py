from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.regulatory_compliance.capital_shortfall.basic.v1"


def solve(text: str, q: dict) -> dict:
    capital = grab(r"\bC\s*=\s*{N}", text)
    required = grab(r"\bR\s*=\s*{N}", text)
    raw = required - capital
    shortfall = raw if raw > 0 else Fraction(0)
    return {"final": shortfall, "slots": {"raw_shortfall_trace": raw}}
