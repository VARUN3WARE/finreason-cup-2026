from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.income_statements.revenue_vs_cogs.basic.v1"


def solve(text: str, q: dict) -> dict:
    revenue = grab(r"reports revenue of {N}\s*USD", text)
    cogs = grab(r"cost of goods sold of {N}\s*USD", text)
    return {"final": revenue - cogs, "slots": {}}
