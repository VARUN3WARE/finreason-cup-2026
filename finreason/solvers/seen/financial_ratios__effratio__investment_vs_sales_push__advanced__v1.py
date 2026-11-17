import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "fp.financial_ratios.effratio.investment_vs_sales_push.advanced.v1"


def solve(text: str, q: dict) -> dict:
    sales = grab(r"[Nn]et sales (?:are|of|were) {N}", text)
    assets = grab(r"current assets (?:are|of|were) {N}", text)
    added = grab(r"Scenario 1 adds {N}", text)
    deducted = grab(r"Scenario 1 adds .*? and then deducts {N}", text)
    m = re.search(rf"Scenario 2 .*?(increases|decreases|raises|reduces|lowers) sales by ({NUMBER}) percent", text)
    if m is None:
        raise ValueError("scenario 2 sales change not found")
    g = Fraction(m.group(2).replace(",", "")) / 100
    if m.group(1) in ("decreases", "reduces", "lowers"):
        g = -g
    t1 = sales / (assets + added - deducted)
    t2 = sales * (1 + g) / assets
    return {"final": t2 - t1, "slots": {"trace_1": t1, "trace_2": t2}}
