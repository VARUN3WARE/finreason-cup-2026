from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.profitratio.dual_margin_gap.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    rev = grab(r"[Rr]evenue (?:is|of) (?:USD )?{N}", text)
    cogs = grab(r"cost of goods sold (?:is|of) (?:USD )?{N}", text)
    ni = grab(r"net income (?:is|of) (?:USD )?{N}", text)
    gross_pct = (rev - cogs) / rev * 100
    net_pct = ni / rev * 100
    return {"final": gross_pct - net_pct, "slots": {"trace_1": gross_pct, "trace_2": net_pct}}
