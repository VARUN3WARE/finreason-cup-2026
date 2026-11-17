from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.stress_testing.sensitivity_of_stock.basic.v1"


def solve(text: str, q: dict) -> dict:
    p = grab(r"\bP\s*=\s*{N}", text)
    shock = grab(r"\bq\s*=\s*{N}\s*percent", text)
    s = grab(r"\bs\s*=\s*{N}", text)
    ratio = shock / 100
    return {"final": p * ratio * s, "slots": {"shock_ratio_trace": ratio}}
