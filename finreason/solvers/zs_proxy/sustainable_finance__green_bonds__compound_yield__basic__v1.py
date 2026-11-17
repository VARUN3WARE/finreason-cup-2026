from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.green_bonds.compound_yield.basic.v1"


def solve(text: str, q: dict) -> dict:
    p = grab(r"principal {N} USD", text)
    r = grab(r"annual yield of {N} percent", text) / 100
    n = grab(r"compounds annually for {N} years?", text)
    assert n.denominator == 1
    factor = (1 + r) ** int(n)
    fv = p * factor
    return {"final": fv - p,
            "slots": {"compound_factor_trace": factor, "future_value_trace": fv}}
