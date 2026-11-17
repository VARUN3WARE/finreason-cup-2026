from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.loanrepay.simple_repayment.basic.v1"


def solve(text: str, q: dict) -> dict:
    principal = grab(r"Principal in USD is {N}", text)
    interest = grab(r"Total interest amount in USD is {N}", text)
    return {"final": principal + interest, "slots": {}}
