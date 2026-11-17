from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.effratio.asset_turnover_with_depreciation.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    sales = grab(r"[Nn]et sales (?:are|of|were) {N}", text)
    base = grab(r"unadjusted asset base (?:is|of|was) {N}", text)
    dep = grab(r"depreciation adjustment of {N}", text)
    adj_base = base - dep  # adjustment "reduces that asset base"
    before = sales / base
    after_t = sales / adj_base
    return {
        "final": after_t - before,
        "slots": {"trace_1": before, "trace_2": adj_base, "trace_3": after_t},
    }
