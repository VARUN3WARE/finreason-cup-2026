from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.irr.after_tax_sale.basic.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"costs {N} USD at time 0", text)
    sale = grab(r"sold for {N} USD", text)
    tax_rate = grab(r"tax equals {N} percent", text) / 100
    basis = cost  # "that amount remains its tax basis"
    gain = sale - basis
    taxable = gain if gain > 0 else Fraction(0)  # tax only on strictly positive gain
    tax = tax_rate * taxable
    after_tax = sale - tax
    irr = after_tax / cost - 1  # one-year holding period
    return {
        "final": irr * 100,
        "slots": {
            "taxable_gain_trace": taxable,
            "gain_tax_trace": tax,
            "after_tax_proceeds_trace": after_tax,
        },
    }
