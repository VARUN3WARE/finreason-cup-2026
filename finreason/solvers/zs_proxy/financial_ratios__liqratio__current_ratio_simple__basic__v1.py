from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.liqratio.current_ratio_simple.basic.v1"


def solve(text: str, q: dict) -> dict:
    ca = grab(r"current assets of {N} USD", text)
    cl = grab(r"current liabilities of {N} USD", text)
    return {"final": ca / cl, "slots": {}}
