from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_appetite.multi_factor_risk_appetite_assessment.advanced.v1"


def solve(text: str, q: dict) -> dict:
    capital = grab(r"Base capital is C\s*=\s*{N}", text)
    a_pct = grab(r"risk appetite is a\s*=\s*{N}\s*percent", text)
    v_pct = grab(r"adjustment is v\s*=\s*{N}\s*percent", text)
    ratio = a_pct / 100
    m = 1 + v_pct / 100
    threshold = capital * ratio * m
    return {"final": threshold, "slots": {"appetite_ratio_trace": ratio, "adjustment_trace": m}}
