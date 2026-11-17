from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.green_bonds.financing_cost_reduction.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    p = grab(r"principal of {N} USD", text)
    rate_pct = grab(r"compounds annually at {N} percent", text)
    n = grab(r"for {N} years?, an integer", text)
    disc_pp = grab(r"reduces that annual rate by {N} percentage points", text)
    assert n.denominator == 1
    adj_pct = rate_pct - disc_pp
    orig_int = p * ((1 + rate_pct / 100) ** int(n) - 1)
    adj_int = p * ((1 + adj_pct / 100) ** int(n) - 1)
    return {"final": orig_int - adj_int,
            "slots": {"original_interest_trace": orig_int,
                      "adjusted_rate_trace": adj_pct,
                      "adjusted_interest_trace": adj_int}}
