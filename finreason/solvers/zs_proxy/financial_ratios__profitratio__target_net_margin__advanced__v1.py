from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.profitratio.target_net_margin.advanced.v1"


def solve(text: str, q: dict) -> dict:
    rev = grab(r"[Rr]evenue (?:is|of) (?:USD )?{N}", text)
    ni = grab(r"current net income (?:is|of) (?:USD )?{N}", text)
    target = grab(r"target net profit margin is {N} percent", text) / 100
    cur_pct = ni / rev * 100
    required = target * rev
    add = required - ni
    if add < 0:
        add = Fraction(0)
    return {"final": add, "slots": {"trace_1": cur_pct, "trace_2": required}}
