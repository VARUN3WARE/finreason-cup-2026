from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.regulatory_compliance.multi_factor_regulatory_compliance.advanced.v1"


def _floor0(x: Fraction) -> Fraction:
    return x if x > 0 else Fraction(0)


def solve(text: str, q: dict) -> dict:
    e = grab(r"\bE\s*=\s*{N}\s*USD", text)
    t = grab(r"\bT\s*=\s*{N}\s*USD", text)
    rate = grab(r"\br\s*=\s*{N}\s*percent", text)
    c = grab(r"\bC\s*=\s*{N}\s*USD", text)
    m = grab(r"\bM\s*=\s*{N}\s*USD", text)
    a = grab(r"\bA\s*=\s*{N}\s*USD", text)
    req = grab(r"\bQ\s*=\s*{N}\s*USD", text)
    penalty = _floor0(e - t) * (rate / 100)
    shortfall = _floor0(m - c)
    gap = _floor0(req - a)
    total = penalty + shortfall + gap
    return {
        "final": total,
        "slots": {"penalty_trace": penalty, "shortfall_trace": shortfall, "gap_trace": gap},
    }
