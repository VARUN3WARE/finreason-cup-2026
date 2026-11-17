from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.green_bonds.synergy_benefit.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    principal = grab(r"has principal {N} USD", text)
    y = grab(r"annual coupon yield of {N} percent", text) / 100
    years = grab(r"compounds annually for {N} years?", text)
    if years.denominator != 1:
        raise ValueError("non-integer years")
    n = int(years)
    savings = grab(r"project saves {N} USD each year", text)
    per_block = grab(r"pays the investor {N} USD for every", text)
    block = grab(r"USD for every {N} USD of annual savings", text)

    interest = principal * ((1 + y) ** n - 1)
    # Fractional savings blocks earn a proportional bonus (no flooring).
    annual_bonus = savings / block * per_block
    total_bonus = annual_bonus * n
    return {
        "final": interest + total_bonus,
        "slots": {
            "interest_earned_trace": interest,
            "annual_bonus_trace": annual_bonus,
            "total_bonus_trace": total_bonus,
        },
    }
