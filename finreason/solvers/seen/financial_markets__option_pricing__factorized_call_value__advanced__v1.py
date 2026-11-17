from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.option_pricing.factorized_call_value.advanced.v1"


def solve(text: str, q: dict) -> dict:
    spot = grab(r"spot price USD {N}", text)
    strike = grab(r"strike USD {N}", text)
    nd1 = grab(r"N\(d1\) = {N}", text)
    nd2 = grab(r"N\(d2\) = {N}", text)
    df = grab(r"strike discount factor = {N}", text)
    weighted_spot = spot * nd1
    discounted_strike = strike * df
    weighted_strike = discounted_strike * nd2
    return {
        "final": weighted_spot - weighted_strike,
        "slots": {
            "weighted_spot_trace": weighted_spot,
            "discounted_strike_trace": discounted_strike,
            "weighted_strike_trace": weighted_strike,
        },
    }
