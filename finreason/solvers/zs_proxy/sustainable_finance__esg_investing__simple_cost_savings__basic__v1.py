from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.esg_investing.simple_cost_savings.basic.v1"


def solve(text: str, q: dict) -> dict:
    monthly = grab(r"saves {N} USD per month", text)
    months = grab(r"measurement period is {N} months", text)
    return {"final": monthly * months, "slots": {}}
