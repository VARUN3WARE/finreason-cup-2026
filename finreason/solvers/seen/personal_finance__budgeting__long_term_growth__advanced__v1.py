from fractions import Fraction

from finreason.nums import grab, ipow

TEMPLATE_ID = "fp.personal_finance.budgeting.long_term_growth.advanced.v1"


def solve(text: str, q: dict) -> dict:
    initial = grab(r"Initial budget in USD is {N}", text)
    ratio = grab(r"Annual growth ratio is {N}", text)
    years = grab(r"Whole-year count is {N}", text)
    factor = 1 + ratio
    multiple = ipow(factor, years)  # whole-year count: exact integer power
    future = initial * multiple
    return {
        "final": future,
        "slots": {"growth_factor": factor, "compounded_multiple": multiple},
    }
