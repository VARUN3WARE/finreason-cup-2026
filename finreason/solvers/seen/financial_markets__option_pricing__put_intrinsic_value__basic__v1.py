from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.option_pricing.put_intrinsic_value.basic.v1"


def solve(text: str, q: dict) -> dict:
    spot = grab(r"spot price USD {N}", text)
    strike = grab(r"strike price USD {N}", text)
    moneyness = strike - spot  # signed strike-minus-spot
    intrinsic = max(moneyness, Fraction(0))
    return {"final": intrinsic, "slots": {"moneyness_trace": moneyness}}
