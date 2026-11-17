from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.rar.sharpe_ratio.basic.v1"


def solve(text: str, q: dict) -> dict:
    rp = grab(r"portfolio return is {N} percent", text)
    rf = grab(r"risk-free rate is {N} percent", text)
    sp = grab(r"portfolio standard deviation is {N} percent", text)
    excess = rp - rf
    sharpe = excess / sp
    return {"final": sharpe, "slots": {"excess_return_trace": excess}}
