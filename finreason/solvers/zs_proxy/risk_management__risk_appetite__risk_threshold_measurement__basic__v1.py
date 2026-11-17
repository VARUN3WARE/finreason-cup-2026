from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_appetite.risk_threshold_measurement.basic.v1"


def solve(text: str, q: dict) -> dict:
    b = grab(r"\bB\s*=\s*{N}", text)             # baseline capital, USD
    a = grab(r"\ba\s*=\s*{N}\s*percent", text)   # risk appetite, percent
    ratio = a / 100
    threshold = b * ratio
    return {"final": threshold, "slots": {"appetite_ratio_trace": ratio}}
