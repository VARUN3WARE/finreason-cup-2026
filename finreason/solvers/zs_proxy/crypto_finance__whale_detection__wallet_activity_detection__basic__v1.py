from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.whale_detection.wallet_activity_detection.basic.v1"


def solve(text: str, q: dict) -> dict:
    transfer = grab(r"observes a transfer of (?:USD )?{N}", text)
    threshold = grab(r"threshold of (?:USD )?{N}", text)
    return {"final": Fraction(transfer) / threshold, "slots": {}}
