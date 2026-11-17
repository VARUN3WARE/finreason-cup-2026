from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.profitratio.net_profit_margin.basic.v1"


def solve(text: str, q: dict) -> dict:
    revenue = grab(r"revenue of {N} USD", text)
    net_income = grab(r"net income of {N} USD", text)
    ratio = net_income / revenue
    return {"final": ratio * 100, "slots": {"trace_1": ratio}}
