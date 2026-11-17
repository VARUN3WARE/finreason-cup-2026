from fractions import Fraction

from finreason.nums import grab, ipow

TEMPLATE_ID = "fp.fintech.digital_banking.monthly_deposit_future_value.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    deposit = grab(r"receives {N} USD at the end of each month", text)
    n = grab(r"for {N} months?", text)
    i = grab(r"monthly compound rate is {N} percent", text) / 100
    growth = ipow(1 + i, n)
    # Ordinary-annuity factor ((1+i)^n - 1)/i; at i == 0 use its limit n.
    factor = (growth - 1) / i if i != 0 else Fraction(n)
    return {
        "final": deposit * factor,
        "slots": {
            "monthly_rate_trace": i,
            "growth_power_trace": growth,
            "annuity_factor_trace": factor,
        },
    }
