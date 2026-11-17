from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.sustainability_reporting.energy_cost_savings.basic.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"energy expenditure of (?:USD )?{N}", text)
    pct = grab(r"reduced it by {N}\s*percent", text)
    ratio = pct / 100
    return {"final": cost * ratio, "slots": {"reduction_ratio_trace": ratio}}
