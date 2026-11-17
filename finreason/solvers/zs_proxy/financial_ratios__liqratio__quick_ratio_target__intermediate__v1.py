from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.liqratio.quick_ratio_target.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    ca = grab(r"Current assets are {N} USD", text)
    inv = grab(r"inventory {N} USD", text)
    prepaid = grab(r"prepaid expenses {N} USD", text)
    cl = grab(r"Current liabilities are {N} USD", text)
    target = grab(r"target quick ratio is {N}", text)
    quick = ca - inv - prepaid
    required = target * cl
    needed = required - quick
    if needed < 0:
        needed = Fraction(0)
    return {"final": needed, "slots": {"trace_1": quick, "trace_2": required}}
