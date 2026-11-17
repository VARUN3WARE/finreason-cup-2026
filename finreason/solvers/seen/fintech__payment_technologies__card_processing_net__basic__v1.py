from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.payment_technologies.card_processing_net.basic.v1"


def solve(text: str, q: dict) -> dict:
    sale = grab(r"sale of {N} USD", text)
    fee_pct = grab(r"merchant discount fee of {N} percent", text)
    keep = 1 - fee_pct / 100
    return {"final": sale * keep, "slots": {"merchant_keep_trace": keep}}
