from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.profitratio.gross_profit_margin.basic.v1"


def solve(text: str, q: dict) -> dict:
    rev = grab(r"[Rr]evenue (?:is|of) (?:USD )?{N}", text)
    cogs = grab(r"cost of goods sold (?:is|of) (?:USD )?{N}", text)
    gp = rev - cogs
    ratio = gp / rev
    return {"final": ratio * 100, "slots": {"trace_1": gp, "trace_2": ratio}}
