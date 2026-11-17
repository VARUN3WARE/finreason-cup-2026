from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.eps.eps_pref_div_weighted.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"Net income is {N}\s*USD", text)
    pref = grab(r"annual preferred dividends are {N}\s*USD", text)
    beg = grab(r"beginning common shares are {N}", text)
    new = grab(r"new common shares issued are {N}", text)
    months = grab(r"outstanding for {N} months?", text)
    common_earn = ni - pref
    wa = beg + new * months / Fraction(12)
    eps = common_earn / wa
    return {"final": eps, "slots": {"trace_1": common_earn, "trace_2": wa}}
