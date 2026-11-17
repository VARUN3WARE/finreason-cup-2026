from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.robo_advisors.monthly_contribution_projection.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    pmt = grab(r"deposits {N} USD at each month end", text)
    n = grab(r"at each month end for {N} months", text)
    r = grab(r"monthly return is {N} percent", text) / 100
    fee = grab(r"ending advisory fee of {N} percent", text) / 100
    if n.denominator != 1:
        raise ValueError("non-integer month count")
    growth = (1 + r) ** int(n)
    factor = (growth - 1) / r if r != 0 else Fraction(int(n))
    before = pmt * factor
    after_fee = before * (1 - fee)
    return {
        "final": after_fee,
        "slots": {
            "growth_power_trace": growth,
            "annuity_factor_trace": factor,
            "before_fee_trace": before,
        },
    }
