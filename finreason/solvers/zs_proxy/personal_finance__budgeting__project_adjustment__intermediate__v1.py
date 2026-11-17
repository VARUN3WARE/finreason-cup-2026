from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.budgeting.project_adjustment.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    current = grab(r"Current budget in USD is {N}", text)
    cost = grab(r"New project cost in USD is {N}", text)
    ratio = grab(r"Contingency ratio is {N}", text)
    contingency = cost * ratio
    requirement = cost + contingency
    adjusted = current + requirement
    return {"final": adjusted, "slots": {"contingency_usd": contingency, "project_requirement_usd": requirement}}
