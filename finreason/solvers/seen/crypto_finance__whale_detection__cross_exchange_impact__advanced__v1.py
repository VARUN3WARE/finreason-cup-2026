from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.whale_detection.cross_exchange_impact.advanced.v1"


def solve(text: str, q: dict) -> dict:
    gross = grab(r"transfer starts at {N}\s*USD", text)
    fee = grab(r"deducts {N}\s*percent", text) / 100
    haircut = grab(r"haircut of {N}\s*percent", text) / 100
    threshold = grab(r"whale threshold is {N}\s*USD", text)
    post_fee = gross * (1 - fee)
    effective = post_fee * (1 - haircut)
    raw = effective - threshold
    final = raw if raw > 0 else Fraction(0)
    return {
        "final": final,
        "slots": {
            "post_fee_trace": post_fee,
            "effective_amount_trace": effective,
            "raw_excess_trace": raw,
        },
    }
