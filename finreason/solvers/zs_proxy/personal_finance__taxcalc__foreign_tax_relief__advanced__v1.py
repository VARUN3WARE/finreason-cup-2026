from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.taxcalc.foreign_tax_relief.advanced.v1"


def solve(text: str, q: dict) -> dict:
    income = grab(r"[Ff]oreign income in USD is {N}", text)
    dom_ratio = grab(r"[Dd]omestic tax ratio is {N}", text)
    foreign_paid = grab(r"[Ff]oreign tax already paid in USD is {N}", text)
    cap_ratio = grab(r"[Rr]elief cap ratio is {N}", text)
    dom_tax = income * dom_ratio                 # domestic tax before relief
    cap = dom_tax * cap_ratio                    # credit cap
    credit = min(foreign_paid, cap)              # allowed credit = smaller of paid and cap
    net = max(dom_tax - credit, Fraction(0))     # net domestic tax floored at zero
    return {
        "final": net,
        "slots": {"domestic_tax_before_relief_usd": dom_tax, "allowed_credit_usd": credit},
    }
