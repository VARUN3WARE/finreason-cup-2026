from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.carbon_credits.credit_purchase.basic.v1"


def solve(text: str, q: dict) -> dict:
    budget = grab(r"budget of {N} USD", text)
    price = grab(r"credit costs {N} USD", text)
    # N = floor(I/P); budget guaranteed divisible, but apply floor literally.
    n = Fraction(budget // price)
    return {"final": n, "slots": {}}
