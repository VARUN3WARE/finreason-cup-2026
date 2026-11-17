from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.eps.eps_weighted_average.basic.v1"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"Net income is {N}\s*USD", text)
    beg = grab(r"beginning common shares are {N}", text)
    new = grab(r"new shares issued are {N}", text)
    months = grab(r"outstanding for {N} months?", text)
    frac_year = months / Fraction(12)
    wa = beg + new * frac_year
    eps = ni / wa
    return {"final": eps, "slots": {"trace_1": frac_year, "trace_2": wa}}
