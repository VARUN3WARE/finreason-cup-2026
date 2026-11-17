from fractions import Fraction

from finreason.nums import grab, real_pow

TEMPLATE_ID = "fp.financial_markets.bond_pricing.zero_coupon_bond_price.basic.v1"


def solve(text: str, q: dict) -> dict:
    face = grab(r"pays USD {N} at maturity", text)
    years = grab(r"at maturity in {N} years?", text)
    y = grab(r"effective annual yield is {N} percent", text) / 100
    base = 1 + y
    if years.denominator == 1:
        denom = base ** int(years)  # exact
    else:
        denom = real_pow(base, years)  # fractional maturity: high-precision
    return {"final": face / denom, "slots": {"discount_denominator_trace": denom}}
