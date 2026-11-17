from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.whale_detection.threshold_adjustment_detection.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    transfer = grab(r"transfer of (?:USD )?{N}", text)
    original = grab(r"original local threshold of (?:USD )?{N}", text)
    adj = grab(r"signed adjustment of {N} percent", text) / 100
    adjusted = original * (1 + adj)
    raw = transfer - adjusted
    final = raw if raw > 0 else Fraction(0)
    return {
        "final": final,
        "slots": {"adjusted_threshold_trace": adjusted, "raw_excess_trace": raw},
    }
