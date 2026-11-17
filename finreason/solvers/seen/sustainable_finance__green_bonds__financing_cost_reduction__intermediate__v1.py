from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.green_bonds.financing_cost_reduction.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    principal = grab(r"financing principal of {N} USD", text)
    rate_pct = grab(r"compounds annually at {N} percent", text)
    years = grab(r"for {N} years?, an integer", text)
    if years.denominator != 1:
        raise ValueError("non-integer years")
    n = int(years)
    cut_pct = grab(r"reduces that annual rate by {N} percentage points?", text)

    adj_pct = rate_pct - cut_pct
    orig_interest = principal * ((1 + rate_pct / 100) ** n - 1)
    adj_interest = principal * ((1 + adj_pct / 100) ** n - 1)
    return {
        "final": orig_interest - adj_interest,
        "slots": {
            "original_interest_trace": orig_interest,
            "adjusted_rate_trace": adj_pct,
            "adjusted_interest_trace": adj_interest,
        },
    }
