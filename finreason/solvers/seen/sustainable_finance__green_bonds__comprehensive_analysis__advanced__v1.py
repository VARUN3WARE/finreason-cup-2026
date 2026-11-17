from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.green_bonds.comprehensive_analysis.advanced.v1"


def solve(text: str, q: dict) -> dict:
    principal = grab(r"has principal {N} USD", text)
    r = grab(r"compounds annually at {N} percent", text) / 100
    years = grab(r"for {N} years?, an integer", text)
    if years.denominator != 1:
        raise ValueError("non-integer years")
    n = int(years)
    credit_rate = grab(r"tax credit of {N} percent", text) / 100
    savings = grab(r"project saves {N} USD per year", text)
    per_block = grab(r"pays {N} USD per proportional", text)
    block = grab(r"per proportional {N}-USD savings block", text)
    reinv_share = grab(r"Each year, {N} percent of that annual interest", text) / 100
    reinv_rate = grab(r"is reinvested at {N} percent annually", text) / 100

    interest = principal * ((1 + r) ** n - 1)
    tax_credit = interest * credit_rate
    # Proportional (non-floored) savings blocks, paid each year for n years.
    total_bonus = savings / block * per_block * n
    # Interest spread evenly over n years; the reinvested slice of year k's interest
    # grows at the reinvestment rate for the remaining n - k full years.
    annual_reinvested = interest / n * reinv_share
    reinvest = sum(
        (annual_reinvested * (1 + reinv_rate) ** (n - k) for k in range(1, n + 1)),
        Fraction(0),
    )
    total = interest + tax_credit + total_bonus + reinvest
    return {
        "final": total,
        "slots": {
            "interest_earned_trace": interest,
            "total_bonus_trace": total_bonus,
            "reinvestment_contribution_trace": reinvest,
        },
    }
