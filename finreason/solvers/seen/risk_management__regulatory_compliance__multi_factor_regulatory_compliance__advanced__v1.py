from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.regulatory_compliance.multi_factor_regulatory_compliance.advanced.v1"


def _floor0(x: Fraction) -> Fraction:
    return x if x > 0 else Fraction(0)


def solve(text: str, q: dict) -> dict:
    exposure = grab(r"\bE\s*=\s*{N}", text)
    threshold = grab(r"\bT\s*=\s*{N}", text)
    rate = grab(r"\br\s*=\s*{N}\s*percent", text) / 100
    capital = grab(r"\bC\s*=\s*{N}", text)
    minimum = grab(r"\bM\s*=\s*{N}", text)
    assets = grab(r"\bA\s*=\s*{N}", text)
    requirement = grab(r"\bQ\s*=\s*{N}", text)
    penalty = _floor0(exposure - threshold) * rate
    shortfall = _floor0(minimum - capital)
    gap = _floor0(requirement - assets)
    return {
        "final": penalty + shortfall + gap,
        "slots": {"penalty_trace": penalty, "shortfall_trace": shortfall, "gap_trace": gap},
    }
