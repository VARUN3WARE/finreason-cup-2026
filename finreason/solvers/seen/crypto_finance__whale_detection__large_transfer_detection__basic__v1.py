from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.whale_detection.large_transfer_detection.basic.v1"


def solve(text: str, q: dict) -> dict:
    transfer = grab(r"transfer of {N}\s*USD", text)
    threshold = grab(r"whale threshold of {N}\s*USD", text)
    raw = transfer - threshold
    final = raw if raw > 0 else Fraction(0)
    return {"final": final, "slots": {"raw_excess_trace": raw}}
