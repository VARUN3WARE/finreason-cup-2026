from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.income_statements.operating_expenses_effect.basic.v1"


def solve(text: str, q: dict) -> dict:
    gp = grab(r"gross profit of {N}\s*USD", text)
    opex = grab(r"total operating expenses of {N}\s*USD", text)
    return {"final": gp - opex, "slots": {}}
