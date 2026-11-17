from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.sensitivity_analysis.multi_asset_portfolio.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    V = grab(r"\bV\s*=\s*{N}", text)
    w = [grab(rf"\bw{i}\s*=\s*{{N}}", text) for i in (1, 2, 3)]
    s = [grab(rf"\bs{i}\s*=\s*{{N}}", text) for i in (1, 2, 3)]
    c = grab(r"\bc\s*=\s*{N}\s*percent", text)
    S = sum((wi * si / 100 for wi, si in zip(w, s)), Fraction(0))
    ratio = c / 100
    change = V * ratio * S
    return {"final": change, "slots": {"weighted_sensitivity_trace": S, "factor_ratio_trace": ratio}}
