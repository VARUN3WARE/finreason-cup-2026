from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.balance_sheets.cash_accounts_payable.basic.v1"


def solve(text: str, q: dict) -> dict:
    cash = grab(r"cash of {N} USD", text)
    ap = grab(r"accounts payable of {N} USD", text)
    # Sign preserved: negative when payables exceed cash.
    return {"final": cash - ap, "slots": {}}
