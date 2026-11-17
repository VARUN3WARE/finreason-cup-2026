from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.taxcalc.flat_tax.basic.v1"


def solve(text: str, q: dict) -> dict:
    income = grab(r"[Tt]axable income in USD is {N}", text)
    ratio = grab(r"[Ff]lat tax ratio is {N}", text)
    tax = income * ratio
    return {"final": tax, "slots": {}}
