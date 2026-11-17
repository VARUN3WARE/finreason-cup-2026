from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.var.time_horizon.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"Portfolio value is V\s*=\s*{N}", text)
    s = grab(r"volatility is s\s*=\s*{N}\s*percent", text)
    t = grab(r"time-scaling scenario multiplier is t\s*=\s*{N}", text)
    z = grab(r"z multiplier is z\s*=\s*{N}", text)
    ratio = s / 100
    scaled = ratio * t * z
    var = v * scaled
    return {
        "final": var,
        "slots": {
            "volatility_ratio_trace": ratio,
            "scaled_volatility_trace": scaled,
        },
    }
