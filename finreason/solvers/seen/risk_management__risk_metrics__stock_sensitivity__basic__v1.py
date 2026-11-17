from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_metrics.stock_sensitivity.basic.v1"


def solve(text: str, q: dict) -> dict:
    p = grab(r"\bP\s*=\s*{N}\s*USD", text)
    d = grab(r"move is d\s*=\s*{N}\s*percent", text)
    ratio = d / 100
    loss = p * ratio  # loss = P*(d/100), as stated (no abs applied)
    return {"final": Fraction(loss), "slots": {"drop_ratio_trace": ratio}}
