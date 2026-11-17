from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.income_statements.inventory_turnover.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    days_in_year = grab(r"For a {N}-day reporting year", text)
    cogs = grab(r"cost of goods sold of {N}\s*USD", text)
    opening = grab(r"opening inventory of {N}\s*USD", text)
    closing = grab(r"closing inventory of {N}\s*USD", text)
    avg_inv = (opening + closing) / 2
    turnover = cogs / avg_inv
    days = days_in_year / turnover
    return {
        "final": days,
        "slots": {
            "average_inventory_trace": avg_inv,
            "inventory_turnover_trace": turnover,
        },
    }
