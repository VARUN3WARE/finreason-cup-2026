from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.option_pricing.factorized_call_value.advanced.v1"


def solve(text: str, q: dict) -> dict:
    spot = grab(r"spot price (?:of )?USD\s*{N}", text)
    strike = grab(r"strike (?:price )?(?:of )?USD\s*{N}", text)
    n1 = grab(r"N\(d1\)\s*=\s*{N}", text)
    n2 = grab(r"N\(d2\)\s*=\s*{N}", text)
    df = grab(r"discount factor\s*=\s*{N}", text)
    weighted_spot = spot * n1
    discounted_strike = strike * df
    weighted_strike = discounted_strike * n2
    call = weighted_spot - weighted_strike
    return {
        "final": call,
        "slots": {
            "weighted_spot_trace": weighted_spot,
            "discounted_strike_trace": discounted_strike,
            "weighted_strike_trace": weighted_strike,
        },
    }
