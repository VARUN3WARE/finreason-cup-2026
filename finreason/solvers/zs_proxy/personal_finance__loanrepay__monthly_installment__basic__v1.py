from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.loanrepay.monthly_installment.basic.v1"


def solve(text: str, q: dict) -> dict:
    total = grab(r"Total repayment in USD is {N}", text)
    months = grab(r"month count is {N}", text)
    return {"final": total / months, "slots": {}}
