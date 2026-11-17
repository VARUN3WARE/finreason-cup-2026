from fractions import Fraction
from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.crypto_finance.global_events_impact.global_macro_strategy.advanced.v1"


def solve(text: str, q: dict) -> dict:
    p0 = grab(r"initial price is {N} USD", text)
    a, b, c = grab_all(r"impacts are {N},\s*{N},?\s*and\s*{N} percent", text)
    floor, cap = grab_all(r"clips their sum between {N} and {N} percent", text)
    raw = a + b + c                      # percent
    clipped = min(max(raw, floor), cap)  # larger with floor, then smaller with cap
    mult = 1 + clipped / 100
    return {
        "final": p0 * mult,
        "slots": {
            "raw_impact_trace": raw,
            "clipped_impact_trace": clipped,
            "price_multiple_trace": mult,
        },
    }
