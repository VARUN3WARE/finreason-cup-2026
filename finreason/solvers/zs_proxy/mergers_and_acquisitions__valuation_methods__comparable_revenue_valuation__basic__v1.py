from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.valuation_methods.comparable_revenue_valuation.basic.v1"


def solve(text: str, q: dict) -> dict:
    revenue = grab(r"Revenue is {N} USD million", text)
    mult = grab(r"revenue multiple is {N} times", text)
    net_debt = grab(r"net debt is {N} USD million", text)
    ev = revenue * mult
    return {"final": ev - net_debt, "slots": {"trace_1": ev}}
