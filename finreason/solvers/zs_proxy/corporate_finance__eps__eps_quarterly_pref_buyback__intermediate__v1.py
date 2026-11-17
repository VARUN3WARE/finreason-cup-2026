from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.eps.eps_quarterly_pref_buyback.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    year_days = grab(r"on a {N}-day year", text)
    ni = grab(r"Net income is {N}\s*USD", text)
    pref_sh = grab(r"preferred shares are {N}", text)
    qdiv = grab(r"quarterly preferred dividend is {N}\s*USD per share", text)
    beg = grab(r"beginning common shares are {N}", text)
    buyback = grab(r"shares repurchased are {N}", text)
    days_absent = grab(r"absent for {N} inclusive days?", text)
    annual_pref = pref_sh * qdiv * 4
    wa = beg - buyback * days_absent / year_days
    eps = (ni - annual_pref) / wa
    return {"final": eps, "slots": {"trace_1": annual_pref, "trace_2": wa}}
