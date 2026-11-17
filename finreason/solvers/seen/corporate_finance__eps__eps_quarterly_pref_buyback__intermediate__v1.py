from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.eps.eps_quarterly_pref_buyback.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"Net income is {N} USD", text)
    pref_sh = grab(r"preferred shares are {N}", text)
    qdiv = grab(r"quarterly preferred dividend is {N} USD per share", text)
    begin = grab(r"beginning common shares are {N}", text)
    bought = grab(r"shares repurchased are {N}", text)
    days = grab(r"absent for {N} inclusive days?", text)
    try:
        year = grab(r"on a {N}-day year", text)
    except ValueError:
        year = Fraction(365)
    annual_pref = pref_sh * qdiv * 4
    wa = begin - bought * days / year
    return {"final": (ni - annual_pref) / wa, "slots": {"trace_1": annual_pref, "trace_2": wa}}
