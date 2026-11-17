"""Stock downside loss: loss = P*(d/100); slot = d/100."""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_metrics.stock_sensitivity.basic.v1"


def solve(text: str, q: dict) -> dict:
    p = grab(r"\bP\s*=\s*{N}", text)
    d = grab(r"downside move is\s+d\s*=\s*{N}\s*percent", text)
    ratio = d / Fraction(100)
    return {"final": p * ratio, "slots": {"drop_ratio_trace": ratio}}
