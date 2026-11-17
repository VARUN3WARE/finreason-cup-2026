import math
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.carbon_credits.credit_purchase.basic.v1"


def solve(text: str, q: dict) -> dict:
    budget = grab(r"hard budget of {N} USD", text)
    price = grab(r"carbon credit costs {N} USD", text)
    # N = floor(I/P); the template guarantees divisibility, floor kept for safety.
    n = Fraction(math.floor(budget / price))
    return {"final": n, "slots": {}}
