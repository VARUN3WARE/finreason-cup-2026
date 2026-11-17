from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.var.stock_return.basic.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"stock value is V\s*=\s*{N}", text)
    l = grab(r"downside scale is l\s*=\s*{N}\s*percent", text)
    z = grab(r"scenario multiplier is z\s*=\s*{N}", text)
    ratio = l / 100
    base = v * ratio
    var = base * z
    return {
        "final": var,
        "slots": {
            "loss_ratio_trace": ratio,
            "base_loss_trace": base,
        },
    }
