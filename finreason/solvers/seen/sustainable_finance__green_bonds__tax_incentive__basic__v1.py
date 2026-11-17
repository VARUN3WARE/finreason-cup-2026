from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.green_bonds.tax_incentive.basic.v1"


def solve(text: str, q: dict) -> dict:
    principal = grab(r"has principal {N} USD", text)
    y = grab(r"annual coupon yield of {N} percent", text) / 100
    years = grab(r"compounds annually for {N} years?", text)
    if years.denominator != 1:
        raise ValueError("non-integer years")
    n = int(years)
    credit_rate = grab(r"tax credit equal to {N} percent", text) / 100

    interest = principal * ((1 + y) ** n - 1)
    credit = interest * credit_rate
    return {
        "final": interest + credit,
        "slots": {"interest_earned_trace": interest, "tax_credit_trace": credit},
    }
