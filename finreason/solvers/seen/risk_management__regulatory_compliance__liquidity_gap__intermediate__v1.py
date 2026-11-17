from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.regulatory_compliance.liquidity_gap.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    assets = grab(r"\bA\s*=\s*{N}", text)
    requirement = grab(r"\bQ\s*=\s*{N}", text)
    raw = requirement - assets
    gap = raw if raw > 0 else Fraction(0)
    return {"final": gap, "slots": {"raw_gap_trace": raw}}
