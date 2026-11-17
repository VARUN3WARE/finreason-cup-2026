from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.taxcalc.standard_deduction.basic.v1"


def solve(text: str, q: dict) -> dict:
    gross = grab(r"[Gg]ross income in USD is {N}", text)
    ded = grab(r"[Ss]tandard deduction in USD is {N}", text)
    ratio = grab(r"[Ff]lat tax ratio is {N}", text)
    taxable = max(gross - ded, Fraction(0))
    tax = taxable * ratio
    return {"final": tax, "slots": {"taxable_income_usd": taxable}}
