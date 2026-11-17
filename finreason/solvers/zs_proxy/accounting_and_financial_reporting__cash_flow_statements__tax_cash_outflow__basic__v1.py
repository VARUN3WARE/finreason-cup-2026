from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.cash_flow_statements.tax_cash_outflow.basic.v1"


def solve(text: str, q: dict) -> dict:
    expense = grab(r"Income tax expense is\s+(?:USD\s+)?{N}", text)
    opening = grab(r"payable are\s+(?:USD\s+)?{N}\s*(?:USD\s+)?at the start", text)
    closing = grab(r"(?:USD\s+)?at the start and\s+(?:USD\s+)?{N}\s*(?:USD\s+)?at the end", text)
    delta = closing - opening
    return {"final": expense - delta, "slots": {"trace_1": delta}}
