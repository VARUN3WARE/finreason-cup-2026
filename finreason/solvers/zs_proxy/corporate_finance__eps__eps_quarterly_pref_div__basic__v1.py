from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.eps.eps_quarterly_pref_div.basic.v1"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"Net income is {N}\s*USD", text)
    pref_sh = grab(r"preferred shares outstanding are {N}", text)
    qdiv = grab(r"preferred dividend is {N}\s*USD per preferred share each quarter", text)
    common = grab(r"common shares outstanding are {N}", text)
    annual_pref = pref_sh * qdiv * 4
    avail = ni - annual_pref
    eps = avail / common
    return {"final": eps, "slots": {"trace_1": annual_pref, "trace_2": avail}}
