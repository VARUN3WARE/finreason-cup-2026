from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.effratio.investment_vs_sales_push.advanced.v1"


def solve(text: str, q: dict) -> dict:
    sales = grab(r"[Cc]urrent net sales (?:are|of|were) {N}", text)
    assets = grab(r"current assets (?:are|of|were) {N}", text)
    add = grab(r"Scenario 1 adds {N}", text)
    ded = grab(r"then deducts {N}", text)
    g = grab(r"increases sales by {N} percent", text) / 100
    s1 = sales / (assets + add - ded)
    s2 = sales * (1 + g) / assets
    return {"final": s2 - s1, "slots": {"trace_1": s1, "trace_2": s2}}
