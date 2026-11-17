from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.due_diligence.due_diligence_after_tax_interest_cost.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    debt = grab(r"debt principal is {N}", text)
    rate = grab(r"interest rate is {N} percent", text) / 100
    tax = grab(r"tax rate is {N} percent", text) / 100
    interest = debt * rate
    keep = 1 - tax
    return {
        "final": interest * keep,
        "slots": {"trace_1": interest, "trace_2": keep},
    }
