from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.income_statements.inventory_turnover.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    cogs = grab(r"cost of goods sold of {N} USD", text)
    opening = grab(r"opening inventory of {N} USD", text)
    closing = grab(r"closing inventory of {N} USD", text)
    try:
        days = grab(r"average days to sell as {N} divided by", text)
    except ValueError:
        days = grab(r"For a {N}-day", text)
    avg_inv = (opening + closing) / 2
    turnover = cogs / avg_inv
    dsi = days / turnover
    return {
        "final": dsi,
        "slots": {
            "average_inventory_trace": avg_inv,
            "inventory_turnover_trace": turnover,
        },
    }
