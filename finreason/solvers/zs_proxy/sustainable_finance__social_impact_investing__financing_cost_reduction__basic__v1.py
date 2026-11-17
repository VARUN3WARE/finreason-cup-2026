from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.social_impact_investing.financing_cost_reduction.basic.v1"


def solve(text: str, q: dict) -> dict:
    rate = grab(r"annual financing rate of {N} percent", text)
    bps = grab(r"reduces that rate by {N} basis points", text)
    pp = bps / 100
    return {"final": rate - pp, "slots": {"reduction_percentage_points_trace": pp}}
