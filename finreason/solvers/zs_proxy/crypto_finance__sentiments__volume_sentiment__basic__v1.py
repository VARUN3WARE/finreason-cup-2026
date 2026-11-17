from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.sentiments.volume_sentiment.basic.v1"


def solve(text: str, q: dict) -> dict:
    sig = grab(r"volume-change signal of\s+{N}", text)
    mult = grab(r"sensitivity multiple of\s+{N}", text)
    return {"final": sig * mult, "slots": {}}
