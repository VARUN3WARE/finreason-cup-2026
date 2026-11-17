from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.sentiments.price_sentiment.basic.v1"


def solve(text: str, q: dict) -> dict:
    signal = grab(r"price-move signal is {N}", text)
    multiple = grab(r"sensitivity multiple is {N}", text)
    return {"final": signal * multiple, "slots": {}}
