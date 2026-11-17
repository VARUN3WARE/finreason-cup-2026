from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.digital_banking.extra_payment_payoff.advanced.v1"


def solve(text: str, q: dict) -> dict:
    principal = grab(r"Initial principal is {N} USD", text)
    monthly = grab(r"scheduled monthly principal payment is {N} USD", text)
    months = grab(r"{N} whole monthly payments? (?:has|have) been made", text)
    extra = grab(r"extra payment of {N} USD", text)
    scheduled = monthly * months
    before = max(principal - scheduled, Fraction(0))
    after = max(before - extra, Fraction(0))
    remaining = after / monthly
    return {
        "final": remaining,
        "slots": {
            "scheduled_paid_trace": scheduled,
            "balance_before_trace": before,
            "balance_after_trace": after,
        },
    }
