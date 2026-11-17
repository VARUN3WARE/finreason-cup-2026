from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.eps.eps_weighted_average.basic.v1"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"Net income is {N} USD", text)
    begin = grab(r"beginning common shares are {N}", text)
    new = grab(r"new shares issued are {N}", text)
    months = grab(r"outstanding for {N} months?", text)
    frac = months / 12
    wa = begin + new * frac
    return {"final": ni / wa, "slots": {"trace_1": frac, "trace_2": wa}}
