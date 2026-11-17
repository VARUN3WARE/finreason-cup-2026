from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.personalinvest.portfolio_allocation.basic.v1"


def solve(text: str, q: dict) -> dict:
    value = grab(r"Portfolio value in USD is {N}", text)
    ratio = grab(r"Target asset ratio is {N}", text)
    asset = value * ratio
    remaining = value * (1 - ratio)
    return {"final": asset, "slots": {"remaining_amount_usd": remaining}}
