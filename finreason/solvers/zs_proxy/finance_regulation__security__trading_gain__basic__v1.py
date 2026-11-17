from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.security.trading_gain.basic.v1"


def solve(text: str, q: dict) -> dict:
    n = grab(r"Share count is {N}", text)
    buy = grab(r"Purchase price per share in USD is {N}", text)
    sell = grab(r"Sale price per share in USD is {N}", text)
    per_share = sell - buy
    total = per_share * n  # framework rounds the final half up to 2 dp
    return {"final": total, "slots": {"gain_per_share": per_share}}
