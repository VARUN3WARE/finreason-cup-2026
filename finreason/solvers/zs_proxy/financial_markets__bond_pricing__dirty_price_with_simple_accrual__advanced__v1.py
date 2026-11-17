from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.bond_pricing.dirty_price_with_simple_accrual.advanced.v1"


def solve(text: str, q: dict) -> dict:
    clean = grab(r"clean price of USD {N}", text)
    face = grab(r"face value USD {N}", text)
    rate = grab(r"annual coupon rate {N} percent", text)
    m = grab(r"{N} equal coupon payments per year", text)
    elapsed = grab(r"Settlement is {N} days after", text)
    period = grab(r"coupon period of {N} days", text)
    annual = face * rate / 100
    per_period = annual / m
    accrued = per_period * (elapsed / period)
    return {
        "final": clean + accrued,
        "slots": {
            "annual_coupon_trace": annual,
            "coupon_per_period_trace": per_period,
            "accrued_interest_trace": accrued,
        },
    }
