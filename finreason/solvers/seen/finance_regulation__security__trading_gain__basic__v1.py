from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.security.trading_gain.basic.v1"


def solve(text: str, q: dict) -> dict:
    shares = grab(r"Share count is {N}", text)
    purchase = grab(r"Purchase price per share in USD is {N}", text)
    sale = grab(r"Sale price per share in USD is {N}", text)
    # Signed gain per share = sale - purchase; total = per-share gain x shares.
    per_share = sale - purchase
    total = per_share * shares  # framework applies the final half-up rounding
    return {"final": total, "slots": {"gain_per_share": per_share}}
