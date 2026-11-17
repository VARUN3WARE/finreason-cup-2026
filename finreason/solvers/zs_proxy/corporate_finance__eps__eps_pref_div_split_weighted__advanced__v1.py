from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.eps.eps_pref_div_split_weighted.advanced.v1"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"Net income is {N}\s*USD", text)
    pref_sh = grab(r"preferred shares are {N}", text)
    qdiv = grab(r"quarterly preferred dividend is {N}\s*USD per preferred share", text)
    beg = grab(r"beginning common shares are {N}", text)
    split = grab(r"stock-split factor is {N}", text)
    annual_pref = pref_sh * qdiv * 4
    adj_shares = beg * split
    eps = (ni - annual_pref) / adj_shares
    return {"final": eps, "slots": {"trace_1": annual_pref, "trace_2": adj_shares}}
