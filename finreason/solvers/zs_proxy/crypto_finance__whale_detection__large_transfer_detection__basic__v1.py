from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.whale_detection.large_transfer_detection.basic.v1"


def solve(text: str, q: dict) -> dict:
    transfer = grab(r"observes a transfer of (?:USD )?{N}", text)
    threshold = grab(r"whale threshold of (?:USD )?{N}", text)
    raw = transfer - threshold
    final = raw if raw > 0 else Fraction(0)
    return {"final": final, "slots": {"raw_excess_trace": raw}}
