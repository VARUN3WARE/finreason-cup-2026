from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.crypto_finance.global_events_impact.global_macro_strategy.advanced.v1"


def solve(text: str, q: dict) -> dict:
    p0 = grab(r"initial price is {N} USD", text)
    liq, geo, reg = grab_all(r"regulatory impacts are {N}, {N},? and {N} percent", text)
    floor, cap = grab_all(r"clips their sum between {N} and {N} percent", text)
    raw = liq + geo + reg
    # "take the larger of that sum and the floor, then the smaller of that result and the cap"
    clipped = min(max(raw, floor), cap)
    multiple = 1 + clipped / 100
    return {
        "final": p0 * multiple,
        "slots": {
            "raw_impact_trace": raw,
            "clipped_impact_trace": clipped,
            "price_multiple_trace": multiple,
        },
    }
