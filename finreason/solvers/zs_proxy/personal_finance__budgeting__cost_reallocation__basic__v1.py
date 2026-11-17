from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.budgeting.cost_reallocation.basic.v1"


def solve(text: str, q: dict) -> dict:
    original = grab(r"Original budget in USD is {N}", text)
    added = grab(r"Added cost in USD is {N}", text)
    savings = grab(r"Savings offset in USD is {N}", text)
    net_added = added - savings  # signed; may be negative or zero
    revised = original + net_added
    return {"final": revised, "slots": {"net_added_cost_usd": net_added}}
