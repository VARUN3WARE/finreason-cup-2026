from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.global_events_impact.market_sentiment_shift.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    cap0 = grab(r"Initial market cap is {N} USD", text)
    ratio = grab(r"sentiment change is {N} percent", text) / 100
    floor = grab(r"policy floor is {N} USD", text)
    raw = cap0 * (1 + ratio)
    published = max(raw, floor)
    return {
        "final": published,
        "slots": {"sentiment_ratio_trace": ratio, "raw_market_cap_trace": raw},
    }
