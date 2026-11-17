from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.taxcalc.itemized_deduction.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    gross = grab(r"[Gg]ross income in USD is {N}", text)
    std = grab(r"[Ss]tandard deduction in USD is {N}", text)
    itm = grab(r"[Ii]temized deduction in USD is {N}", text)
    ratio = grab(r"[Ff]lat tax ratio is {N}", text)
    chosen = max(std, itm)                        # larger deduction (tie -> same value)
    taxable = max(gross - chosen, Fraction(0))
    tax = taxable * ratio
    return {"final": tax, "slots": {"chosen_deduction_usd": chosen, "taxable_income_usd": taxable}}
