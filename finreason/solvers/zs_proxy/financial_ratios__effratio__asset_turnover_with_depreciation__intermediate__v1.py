from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.effratio.asset_turnover_with_depreciation.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    sales = grab(r"[Nn]et sales (?:are|of|were) {N}", text)
    base = grab(r"unadjusted asset base (?:is|of|was) {N}", text)
    dep = grab(r"depreciation adjustment of {N}", text)
    adj_base = base - dep
    t0 = sales / base
    t1 = sales / adj_base
    return {"final": t1 - t0, "slots": {"trace_1": t0, "trace_2": adj_base, "trace_3": t1}}
