from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.profitratio.net_profit_margin.basic.v1"


def solve(text: str, q: dict) -> dict:
    rev = grab(r"[Rr]evenue (?:is|of) (?:USD )?{N}", text)
    ni = grab(r"net income (?:is|of) (?:USD )?{N}", text)
    ratio = ni / rev
    return {"final": ratio * 100, "slots": {"trace_1": ratio}}
