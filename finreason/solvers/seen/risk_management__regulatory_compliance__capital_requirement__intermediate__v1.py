from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.regulatory_compliance.capital_requirement.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    capital = grab(r"\bC\s*=\s*{N}", text)
    minimum = grab(r"\bM\s*=\s*{N}", text)
    raw = minimum - capital
    deficiency = raw if raw > 0 else Fraction(0)
    return {"final": deficiency, "slots": {"raw_deficiency_trace": raw}}
