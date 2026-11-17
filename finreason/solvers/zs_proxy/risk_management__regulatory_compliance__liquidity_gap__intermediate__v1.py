from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.regulatory_compliance.liquidity_gap.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    a = grab(r"\bA\s*=\s*{N}\s*USD", text)
    req = grab(r"\bQ\s*=\s*{N}\s*USD", text)
    raw = req - a
    gap = raw if raw > 0 else Fraction(0)
    return {"final": gap, "slots": {"raw_gap_trace": raw}}
