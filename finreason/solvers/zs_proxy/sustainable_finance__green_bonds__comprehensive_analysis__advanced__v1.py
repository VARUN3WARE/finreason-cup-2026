from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.green_bonds.comprehensive_analysis.advanced.v1"


def solve(text: str, q: dict) -> dict:
    p = grab(r"principal {N} USD", text)
    r = grab(r"compounds annually at {N} percent", text) / 100
    n = grab(r"for {N} years?, an integer", text)
    credit_rate = grab(r"tax credit of {N} percent", text) / 100
    savings = grab(r"saves {N} USD per year", text)
    per_block = grab(r"pays {N} USD per proportional", text)
    block = grab(r"per proportional {N}-USD savings block", text)
    reinv_share = grab(r"Each year, {N} percent of that annual interest", text) / 100
    reinv_rate = grab(r"is reinvested at {N} percent annually", text) / 100
    assert n.denominator == 1
    years = int(n)

    interest = p * ((1 + r) ** years - 1)
    credit = interest * credit_rate
    total_bonus = savings / block * per_block * years

    # Interest evenly distributed across years; each year's reinvested share is
    # placed at that year-end and grows for the remaining full years (n - k).
    annual_interest = interest / years
    reinvested = annual_interest * reinv_share
    reinvest_contrib = sum((reinvested * (1 + reinv_rate) ** (years - k)
                            for k in range(1, years + 1)), Fraction(0))

    total = interest + credit + total_bonus + reinvest_contrib
    return {"final": total,
            "slots": {"interest_earned_trace": interest,
                      "total_bonus_trace": total_bonus,
                      "reinvestment_contribution_trace": reinvest_contrib}}
