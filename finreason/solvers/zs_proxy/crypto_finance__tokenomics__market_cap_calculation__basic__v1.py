from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.tokenomics.market_cap_calculation.basic.v1"


def solve(text: str, q: dict) -> dict:
    supply = grab(r"has {N} units", text)
    price = grab(r"price of {N} USD per token", text)
    return {"final": supply * price, "slots": {}}
