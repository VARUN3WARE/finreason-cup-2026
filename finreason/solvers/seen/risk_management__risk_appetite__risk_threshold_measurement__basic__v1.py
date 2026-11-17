from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_appetite.risk_threshold_measurement.basic.v1"


def solve(text: str, q: dict) -> dict:
    baseline = grab(r"Baseline capital is B\s*=\s*{N}", text)
    a_pct = grab(r"risk appetite is a\s*=\s*{N}\s*percent", text)
    ratio = a_pct / 100
    threshold = baseline * ratio
    return {"final": threshold, "slots": {"appetite_ratio_trace": ratio}}
