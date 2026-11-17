from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.regulatory_compliance.compliance_penalty.basic.v1"


def solve(text: str, q: dict) -> dict:
    exposure = grab(r"\bE\s*=\s*{N}", text)
    threshold = grab(r"\bT\s*=\s*{N}", text)
    rate = grab(r"\br\s*=\s*{N}\s*percent", text) / 100
    raw = exposure - threshold
    excess = raw if raw > 0 else Fraction(0)
    return {
        "final": excess * rate,
        "slots": {"raw_excess_trace": raw, "excess_trace": excess},
    }
