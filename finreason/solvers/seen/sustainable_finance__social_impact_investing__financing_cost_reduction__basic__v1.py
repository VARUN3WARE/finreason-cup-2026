from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.social_impact_investing.financing_cost_reduction.basic.v1"


def solve(text: str, q: dict) -> dict:
    rate = grab(r"annual financing rate of {N} percent", text)
    bps = grab(r"reduces that rate by {N} basis points", text)
    reduction_pp = bps / 100  # 100 bp = 1 percentage point
    return {
        "final": rate - reduction_pp,
        "slots": {"reduction_percentage_points_trace": reduction_pp},
    }
