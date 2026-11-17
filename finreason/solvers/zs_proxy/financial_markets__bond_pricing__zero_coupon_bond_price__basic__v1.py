from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.bond_pricing.zero_coupon_bond_price.basic.v1"


def solve(text: str, q: dict) -> dict:
    face = grab(r"pays USD {N} at maturity", text)
    years = grab(r"at maturity in {N} years?", text)
    y = grab(r"effective annual yield is {N} percent", text)
    if years.denominator != 1:
        raise ValueError("non-integer years")
    denom = (1 + y / 100) ** int(years)
    return {"final": face / denom, "slots": {"discount_denominator_trace": denom}}
