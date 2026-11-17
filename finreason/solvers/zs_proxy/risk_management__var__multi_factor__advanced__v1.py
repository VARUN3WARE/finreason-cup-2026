from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.var.multi_factor.advanced.v1"


def solve(text: str, q: dict) -> dict:
    V = grab(r"Portfolio value is V\s*=\s*{N}", text)
    a = grab(r"market risk is a\s*=\s*{N}\s*percent", text)
    b = grab(r"credit risk is b\s*=\s*{N}\s*percent", text)
    qq = grab(r"liquidity risk is q\s*=\s*{N}\s*percent", text)
    t = grab(r"multiplier is t\s*=\s*{N}", text)
    c = grab(r"confidence is c\s*=\s*{N}\s*percent", text)
    R = (a + b + qq) / 3                              # percent
    m = 1 + (100 - c) / 100
    var = V * (R / 100) * t * m
    return {"final": var, "slots": {"combined_risk_trace": R, "confidence_multiplier_trace": m}}
