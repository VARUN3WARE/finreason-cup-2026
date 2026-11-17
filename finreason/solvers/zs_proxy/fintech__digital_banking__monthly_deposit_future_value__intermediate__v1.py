from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.digital_banking.monthly_deposit_future_value.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    deposit = grab(r"receives {N} USD at the end of each month", text)
    n = grab(r"for {N} months?", text)
    i = grab(r"monthly compound rate is {N} percent", text) / 100
    if n.denominator != 1:
        raise ValueError("non-integer month count")
    growth = (1 + i) ** int(n)
    factor = (growth - 1) / i if i != 0 else Fraction(n)
    return {
        "final": deposit * factor,
        "slots": {
            "monthly_rate_trace": i,
            "growth_power_trace": growth,
            "annuity_factor_trace": factor,
        },
    }
