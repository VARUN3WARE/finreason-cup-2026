from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.green_bonds.tax_incentive.basic.v1"


def solve(text: str, q: dict) -> dict:
    p = grab(r"principal {N} USD", text)
    r = grab(r"annual coupon yield of {N} percent", text) / 100
    n = grab(r"compounds annually for {N} years?", text)
    c = grab(r"tax credit equal to {N} percent", text) / 100
    assert n.denominator == 1
    interest = p * ((1 + r) ** int(n) - 1)
    credit = interest * c
    return {"final": interest + credit,
            "slots": {"interest_earned_trace": interest, "tax_credit_trace": credit}}
