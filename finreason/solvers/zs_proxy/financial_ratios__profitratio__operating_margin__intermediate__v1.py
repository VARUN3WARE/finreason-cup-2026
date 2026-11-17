from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.profitratio.operating_margin.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    rev = grab(r"[Rr]evenue (?:is|of) (?:USD )?{N}", text)
    cogs = grab(r"cost of goods sold (?:is|of) (?:USD )?{N}", text)
    opex = grab(r"operating expenses excluding cost of goods sold (?:are|is|of) (?:USD )?{N}", text)
    gp = rev - cogs
    op = gp - opex
    return {"final": op / rev * 100, "slots": {"trace_1": gp, "trace_2": op}}
