from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.stress_testing.multi_asset_portfolio.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"Portfolio value is V\s*=\s*{N}", text)
    w1 = grab(r"\bw1\s*=\s*{N}", text)
    w2 = grab(r"\bw2\s*=\s*{N}", text)
    w3 = grab(r"\bw3\s*=\s*{N}", text)
    s1 = grab(r"\bs1\s*=\s*{N}", text)
    s2 = grab(r"\bs2\s*=\s*{N}", text)
    s3 = grab(r"\bs3\s*=\s*{N}", text)
    c = grab(r"stress change is c\s*=\s*{N}\s*percent", text)
    s = w1 * s1 / 100 + w2 * s2 / 100 + w3 * s3 / 100
    ratio = c / 100
    impact = v * ratio * s
    return {
        "final": impact,
        "slots": {
            "weighted_sensitivity_trace": s,
            "factor_ratio_trace": ratio,
        },
    }
