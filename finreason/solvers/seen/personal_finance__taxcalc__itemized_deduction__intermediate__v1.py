from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.taxcalc.itemized_deduction.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    gross = grab(r"Gross income in USD is {N}", text)
    std = grab(r"Standard deduction in USD is {N}", text)
    itemized = grab(r"Itemized deduction in USD is {N}", text)
    ratio = grab(r"Flat tax ratio is {N}", text)
    # Chosen deduction is the larger deduction (on a tie both are equal).
    chosen = max(std, itemized)
    taxable = max(gross - chosen, Fraction(0))
    return {
        "final": taxable * ratio,
        "slots": {"chosen_deduction_usd": chosen, "taxable_income_usd": taxable},
    }
