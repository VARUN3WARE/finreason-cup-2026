from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_appetite.risk_adjusted_return.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    capital = grab(r"Capital is C\s*=\s*{N}", text)
    f_pct = grab(r"risk factor is f\s*=\s*{N}\s*percent", text)
    p_pct = grab(r"risk premium is p\s*=\s*{N}\s*percent", text)
    f_ratio = f_pct / 100
    p_ratio = p_pct / 100
    allocation = capital * f_ratio * p_ratio
    return {
        "final": allocation,
        "slots": {"factor_ratio_trace": f_ratio, "premium_ratio_trace": p_ratio},
    }
