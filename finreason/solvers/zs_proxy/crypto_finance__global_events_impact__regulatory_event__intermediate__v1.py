from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.global_events_impact.regulatory_event.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    p0 = grab(r"initial asset price is {N} USD", text)
    ratio = grab(r"the impact is {N} percent", text) / 100
    mult = 1 + ratio
    return {
        "final": p0 * mult,
        "slots": {"impact_ratio_trace": ratio, "price_multiple_trace": mult},
    }
