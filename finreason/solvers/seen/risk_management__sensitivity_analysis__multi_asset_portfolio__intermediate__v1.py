from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.sensitivity_analysis.multi_asset_portfolio.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"\bV\s*=\s*{N}", text)
    w = [grab(r"\bw%d\s*=\s*{N}" % i, text) for i in (1, 2, 3)]
    s = [grab(r"\bs%d\s*=\s*{N}" % i, text) for i in (1, 2, 3)]
    c = grab(r"\bc\s*=\s*{N}", text)
    # S = sum(w_i * s_i / 100); change = V * (c/100) * S, signed, no intermediate rounding.
    weighted = sum((wi * si / 100 for wi, si in zip(w, s)), Fraction(0))
    ratio = c / 100
    change = v * ratio * weighted
    return {
        "final": change,
        "slots": {
            "weighted_sensitivity_trace": weighted,
            "factor_ratio_trace": ratio,
        },
    }
