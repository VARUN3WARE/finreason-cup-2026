from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.regulatory_compliance.capital_shortfall.basic.v1"


def solve(text: str, q: dict) -> dict:
    c = grab(r"\bC\s*=\s*{N}\s*USD", text)
    r = grab(r"\bR\s*=\s*{N}\s*USD", text)
    raw = r - c
    shortfall = raw if raw > 0 else Fraction(0)
    return {"final": shortfall, "slots": {"raw_shortfall_trace": raw}}
