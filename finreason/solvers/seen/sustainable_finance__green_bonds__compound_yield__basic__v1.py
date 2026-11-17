from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.green_bonds.compound_yield.basic.v1"


def solve(text: str, q: dict) -> dict:
    principal = grab(r"has principal {N} USD", text)
    y = grab(r"annual yield of {N} percent", text) / 100
    years = grab(r"compounds annually for {N} years?", text)
    if years.denominator != 1:
        raise ValueError("non-integer years")
    factor = (1 + y) ** int(years)
    fv = principal * factor
    return {
        "final": fv - principal,
        "slots": {"compound_factor_trace": factor, "future_value_trace": fv},
    }
