from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.regulatory_compliance.capital_requirement.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    c = grab(r"\bC\s*=\s*{N}\s*USD", text)
    m = grab(r"\bM\s*=\s*{N}\s*USD", text)
    raw = m - c
    deficiency = raw if raw > 0 else Fraction(0)
    return {"final": deficiency, "slots": {"raw_deficiency_trace": raw}}
