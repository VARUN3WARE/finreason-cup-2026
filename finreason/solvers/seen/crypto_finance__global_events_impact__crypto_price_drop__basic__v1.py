from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.global_events_impact.crypto_price_drop.basic.v1"


def solve(text: str, q: dict) -> dict:
    p0 = grab(r"pre-event price is {N} USD", text)
    drop = grab(r"drop is {N} percent", text) / 100
    retention = 1 - drop
    return {"final": p0 * retention, "slots": {"retention_ratio_trace": retention}}
