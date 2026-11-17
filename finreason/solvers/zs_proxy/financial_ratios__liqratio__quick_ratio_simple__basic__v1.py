from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.liqratio.quick_ratio_simple.basic.v1"


def solve(text: str, q: dict) -> dict:
    ca = grab(r"Current assets are {N} USD", text)
    inv = grab(r"inventory of {N} USD", text)
    cl = grab(r"current liabilities are {N} USD", text)
    quick_assets = ca - inv
    return {"final": quick_assets / cl, "slots": {"trace_1": quick_assets}}
