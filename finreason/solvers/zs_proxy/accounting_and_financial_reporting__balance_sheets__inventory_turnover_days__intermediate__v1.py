from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.balance_sheets.inventory_turnover_days.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    opening = grab(r"Opening inventory is {N} USD", text)
    purchases = grab(r"purchases are {N} USD", text)
    closing = grab(r"closing inventory is {N} USD", text)
    days = grab(r"use a {N}-day year", text)
    cogs = opening + purchases - closing
    avg_inv = (opening + closing) / 2
    turnover = cogs / avg_inv
    return {
        "final": days / turnover,
        "slots": {"trace_1": cogs, "trace_2": avg_inv, "trace_3": turnover},
    }
