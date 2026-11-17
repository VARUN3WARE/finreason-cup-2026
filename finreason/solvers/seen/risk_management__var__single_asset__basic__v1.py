from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.var.single_asset.basic.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"portfolio value is V\s*=\s*{N}", text)
    s = grab(r"volatility is s\s*=\s*{N}\s*percent", text)
    t = grab(r"multiplier is t\s*=\s*{N}", text)
    c = grab(r"confidence is c\s*=\s*{N}\s*percent", text)
    ratio = s / 100
    m = 1 + (100 - c) / 100
    var = v * ratio * t * m
    return {
        "final": var,
        "slots": {
            "volatility_ratio_trace": ratio,
            "confidence_multiplier_trace": m,
        },
    }
