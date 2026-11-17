from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.regulatory_compliance.compliance_penalty.basic.v1"


def solve(text: str, q: dict) -> dict:
    e = grab(r"\bE\s*=\s*{N}\s*USD", text)
    t = grab(r"\bT\s*=\s*{N}\s*USD", text)
    rate = grab(r"\br\s*=\s*{N}\s*percent", text)
    raw = e - t
    excess = raw if raw > 0 else Fraction(0)
    penalty = excess * (rate / 100)
    return {"final": penalty, "slots": {"raw_excess_trace": raw, "excess_trace": excess}}
