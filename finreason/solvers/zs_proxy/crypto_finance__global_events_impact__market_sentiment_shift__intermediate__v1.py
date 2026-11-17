from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.global_events_impact.market_sentiment_shift.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    cap0 = grab(r"[Ii]nitial market cap is {N} USD", text)
    ratio = grab(r"sentiment change is {N} percent", text) / 100
    floor = grab(r"policy floor is {N} USD", text)
    raw = cap0 * (1 + ratio)
    return {
        "final": max(raw, floor),
        "slots": {"sentiment_ratio_trace": ratio, "raw_market_cap_trace": raw},
    }
