from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.due_diligence.due_diligence_after_tax_interest_cost.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    debt = grab(r"debt principal is {N}", text)
    rate = grab(r"annual interest rate is {N} percent", text) / 100
    tax = grab(r"corporate tax rate is {N} percent", text) / 100
    interest = debt * rate
    one_minus_t = Fraction(1) - tax
    return {"final": interest * one_minus_t,
            "slots": {"trace_1": interest, "trace_2": one_minus_t}}
