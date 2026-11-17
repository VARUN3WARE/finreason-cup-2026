from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.taxcalc.standard_deduction.basic.v1"


def solve(text: str, q: dict) -> dict:
    gross = grab(r"Gross income in USD is {N}", text)
    deduction = grab(r"Standard deduction in USD is {N}", text)
    ratio = grab(r"Flat tax ratio is {N}", text)
    taxable = max(gross - deduction, Fraction(0))
    return {"final": taxable * ratio, "slots": {"taxable_income_usd": taxable}}
