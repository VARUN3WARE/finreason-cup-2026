from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.green_bonds.synergy_benefit.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    p = grab(r"principal {N} USD", text)
    r = grab(r"annual coupon yield of {N} percent", text) / 100
    n = grab(r"compounds annually for {N} years?", text)
    savings = grab(r"saves {N} USD each year", text)
    per_block = grab(r"pays the investor {N} USD for every", text)
    block = grab(r"for every {N} USD of annual savings", text)
    assert n.denominator == 1
    interest = p * ((1 + r) ** int(n) - 1)
    annual_bonus = savings / block * per_block   # proportional (fractional) blocks
    total_bonus = annual_bonus * n
    return {"final": interest + total_bonus,
            "slots": {"interest_earned_trace": interest,
                      "annual_bonus_trace": annual_bonus,
                      "total_bonus_trace": total_bonus}}
