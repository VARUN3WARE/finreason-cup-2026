from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.var.multi_factor.advanced.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"Portfolio value is V\s*=\s*{N}", text)
    a = grab(r"market risk is a\s*=\s*{N}\s*percent", text)
    b = grab(r"credit risk is b\s*=\s*{N}\s*percent", text)
    lq = grab(r"liquidity risk is q\s*=\s*{N}\s*percent", text)
    t = grab(r"multiplier is t\s*=\s*{N}", text)
    c = grab(r"confidence is c\s*=\s*{N}\s*percent", text)
    r = (a + b + lq) / 3  # percent
    m = 1 + (100 - c) / 100
    var = v * (r / 100) * t * m
    return {
        "final": var,
        "slots": {
            "combined_risk_trace": r,
            "confidence_multiplier_trace": m,
        },
    }
