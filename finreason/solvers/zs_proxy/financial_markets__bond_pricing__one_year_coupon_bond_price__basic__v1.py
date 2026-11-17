from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.bond_pricing.one_year_coupon_bond_price.basic.v1"


def solve(text: str, q: dict) -> dict:
    face = grab(r"face value USD {N}", text)
    rate = grab(r"annual coupon rate of {N} percent", text)
    y = grab(r"effective annual yield of {N} percent", text)
    coupon = face * rate / 100
    cf = face + coupon
    return {
        "final": cf / (1 + y / 100),
        "slots": {"annual_coupon_trace": coupon, "maturity_cash_flow_trace": cf},
    }
