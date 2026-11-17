from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.cash_flow_statements.closing_cash_balance.basic.v1"


def solve(text: str, q: dict) -> dict:
    opening = grab(r"Opening cash is {N}", text)
    cfo = grab(r"[Nn]et operating cash flow is {N}", text)
    cfi = grab(r"[Nn]et investing cash flow is {N}", text)
    cff = grab(r"[Nn]et financing cash flow is {N}", text)
    # Flows are signed (positive inflow, negative outflow): simply add.
    return {"final": Fraction(opening + cfo + cfi + cff), "slots": {}}
