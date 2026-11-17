from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.eps.eps_pref_div_weighted.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"Net income is {N} USD", text)
    pref = grab(r"annual preferred dividends are {N} USD", text)
    begin = grab(r"beginning common shares are {N}", text)
    new = grab(r"new common shares issued are {N}", text)
    months = grab(r"outstanding for {N} months?", text)
    avail = ni - pref
    wa = begin + new * months / 12
    return {"final": avail / wa, "slots": {"trace_1": avail, "trace_2": wa}}
