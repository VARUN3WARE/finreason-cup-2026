from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.balance_sheets.balance_sheet_equation.basic.v1"


def solve(text: str, q: dict) -> dict:
    assets = grab(r"total assets of {N} USD", text)
    liabilities = grab(r"total liabilities of {N} USD", text)
    # Equity = Assets - Liabilities; sign preserved (negative if liabilities exceed assets).
    return {"final": assets - liabilities, "slots": {}}
