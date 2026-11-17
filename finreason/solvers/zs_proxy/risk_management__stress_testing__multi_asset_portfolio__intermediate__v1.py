from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.stress_testing.multi_asset_portfolio.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"\bV\s*=\s*{N}", text)
    w = [grab(r"\bw%d\s*=\s*{N}" % i, text) for i in (1, 2, 3)]
    s = [grab(r"\bs%d\s*=\s*{N}" % i, text) for i in (1, 2, 3)]
    c = grab(r"\bc\s*=\s*{N}\s*percent", text)
    S = sum((wi * si / 100 for wi, si in zip(w, s)), Fraction(0))
    ratio = c / 100
    impact = v * ratio * S
    return {"final": impact,
            "slots": {"weighted_sensitivity_trace": S, "factor_ratio_trace": ratio}}
