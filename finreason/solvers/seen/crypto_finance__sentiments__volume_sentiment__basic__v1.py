from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.sentiments.volume_sentiment.basic.v1"


def solve(text: str, q: dict) -> dict:
    signal = grab(r"volume-change signal of {N}", text)
    multiple = grab(r"sensitivity multiple of {N}", text)
    return {"final": signal * multiple, "slots": {}}
