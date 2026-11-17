from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.var.multi_asset.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"Portfolio value is V\s*=\s*{N}", text)
    w1 = grab(r"\bw1\s*=\s*{N}\s*percent", text)
    w2 = grab(r"\bw2\s*=\s*{N}\s*percent", text)
    w3 = grab(r"\bw3\s*=\s*{N}\s*percent", text)
    s1 = grab(r"\bs1\s*=\s*{N}\s*percent", text)
    s2 = grab(r"\bs2\s*=\s*{N}\s*percent", text)
    s3 = grab(r"\bs3\s*=\s*{N}\s*percent", text)
    t = grab(r"multiplier is t\s*=\s*{N}", text)
    c = grab(r"confidence is c\s*=\s*{N}\s*percent", text)
    # S = (w1*s1 + w2*s2 + w3*s3)/100, in percent
    s_pct = (w1 * s1 + w2 * s2 + w3 * s3) / 100
    ratio = s_pct / 100
    m = 1 + (100 - c) / 100
    var = v * ratio * t * m
    return {
        "final": var,
        "slots": {
            "weighted_volatility_trace": s_pct,
            "weighted_ratio_trace": ratio,
            "confidence_multiplier_trace": m,
        },
    }
