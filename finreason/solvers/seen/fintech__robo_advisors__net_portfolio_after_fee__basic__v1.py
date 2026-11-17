from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.robo_advisors.net_portfolio_after_fee.basic.v1"


def solve(text: str, q: dict) -> dict:
    value = grab(r"portfolio is worth {N}", text)
    fee = grab(r"advisory fee of {N}\s*percent", text) / 100
    keep = 1 - fee
    return {"final": value * keep, "slots": {"keep_ratio_trace": keep}}
