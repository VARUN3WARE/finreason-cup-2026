from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.valuation_methods.ebitda_multiple_valuation.basic.v1"


def solve(text: str, q: dict) -> dict:
    ebitda = grab(r"EBITDA is {N} USD million", text)
    mult = grab(r"EBITDA multiple is {N} times", text)
    net_debt = grab(r"net debt is {N} USD million", text)
    ev = ebitda * mult
    return {"final": ev - net_debt, "slots": {"trace_1": ev}}
