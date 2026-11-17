from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.cash_flow_statements.tax_cash_outflow.basic.v1"


def solve(text: str, q: dict) -> dict:
    expense = grab(r"[Ii]ncome tax expense is {N}", text)
    opening = grab(r"payable are {N} USD at the start", text)
    closing = grab(r"USD at the start and {N} USD at the end", text)
    change = closing - opening
    return {"final": Fraction(expense - change), "slots": {"trace_1": change}}
