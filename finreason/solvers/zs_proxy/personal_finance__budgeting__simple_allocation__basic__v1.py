from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.budgeting.simple_allocation.basic.v1"


def solve(text: str, q: dict) -> dict:
    income = grab(r"Monthly income in USD is {N}", text)
    ratio = grab(r"Allocation ratio is {N}", text)
    allocation = income * ratio
    return {"final": allocation, "slots": {}}
