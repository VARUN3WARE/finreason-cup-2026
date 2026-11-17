from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.taxcalc.foreign_tax_relief.advanced.v1"


def solve(text: str, q: dict) -> dict:
    income = grab(r"Foreign income in USD is {N}", text)
    dom_ratio = grab(r"Domestic tax ratio is {N}", text)
    foreign_paid = grab(r"Foreign tax already paid in USD is {N}", text)
    cap_ratio = grab(r"Relief cap ratio is {N}", text)
    dom_tax = income * dom_ratio
    cap = dom_tax * cap_ratio
    credit = min(foreign_paid, cap)
    net = max(dom_tax - credit, Fraction(0))
    return {
        "final": net,
        "slots": {
            "domestic_tax_before_relief_usd": dom_tax,
            "allowed_credit_usd": credit,
        },
    }
