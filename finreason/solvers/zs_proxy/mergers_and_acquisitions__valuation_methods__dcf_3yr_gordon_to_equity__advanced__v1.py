from fractions import Fraction
from finreason.nums import grab_all, grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.valuation_methods.dcf_3yr_gordon_to_equity.advanced.v1"


def solve(text: str, q: dict) -> dict:
    f1, f2, f3 = grab_all(r"Years 1 through 3 are {N}, {N}, and {N} USD million", text)
    r = grab(r"discount rate is {N} percent", text) / 100
    g = grab(r"terminal growth rate is {N} percent", text) / 100
    debt = grab(r"total debt is {N} USD million", text)
    cash = grab(r"cash is {N} USD million", text)
    d = 1 + r
    pv_fcf = f1 / d + f2 / d ** 2 + f3 / d ** 3
    tv = f3 * (1 + g) / (r - g)
    pv_tv = tv / d ** 3
    ev = pv_fcf + pv_tv
    net_debt = debt - cash
    return {"final": ev - net_debt, "slots": {"trace_1": tv, "trace_2": ev}}
