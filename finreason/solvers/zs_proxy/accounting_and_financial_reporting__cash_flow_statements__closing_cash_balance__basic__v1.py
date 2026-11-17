from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.cash_flow_statements.closing_cash_balance.basic.v1"


def solve(text: str, q: dict) -> dict:
    opening = grab(r"Opening cash is\s+(?:USD\s+)?{N}", text)
    op = grab(r"net operating cash flow is\s+(?:USD\s+)?{N}", text.lower())
    inv = grab(r"net investing cash flow is\s+(?:USD\s+)?{N}", text.lower())
    fin = grab(r"net financing cash flow is\s+(?:USD\s+)?{N}", text.lower())
    # Each net flow is signed (positive = inflow, negative = outflow).
    return {"final": opening + op + inv + fin, "slots": {}}
