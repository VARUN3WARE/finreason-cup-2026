from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.sentiments.price_sentiment.basic.v1"


def solve(text: str, q: dict) -> dict:
    sig = grab(r"price-move signal is\s+{N}", text)
    mult = grab(r"sensitivity multiple is\s+{N}", text)
    return {"final": sig * mult, "slots": {}}
