from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.robo_advisors.monthly_contribution_projection.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    pmt = grab(r"deposits {N}\s*[A-Za-z]*\s*at each month end", text)
    months = grab(r"for {N}\s*months?", text)
    r = grab(r"monthly return is {N}\s*percent", text) / 100
    fee = grab(r"ending advisory fee of {N}\s*percent", text) / 100
    if months.denominator != 1:
        raise ValueError(f"non-integer month count {months}")
    n = int(months)
    growth = (1 + r) ** n
    # Ordinary-annuity factor ((1+r)^n - 1)/r; limit n when r == 0.
    factor = (growth - 1) / r if r != 0 else Fraction(n)
    before_fee = pmt * factor
    after_fee = before_fee * (1 - fee)
    return {
        "final": after_fee,
        "slots": {
            "growth_power_trace": growth,
            "annuity_factor_trace": factor,
            "before_fee_trace": before_fee,
        },
    }
