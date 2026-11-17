from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.taxcalc.flat_tax.basic.v1"


def solve(text: str, q: dict) -> dict:
    income = grab(r"Taxable income in USD is {N}", text)
    ratio = grab(r"Flat tax ratio is {N}", text)
    # Exact product; framework applies the final half-up rounding.
    return {"final": income * ratio, "slots": {}}
