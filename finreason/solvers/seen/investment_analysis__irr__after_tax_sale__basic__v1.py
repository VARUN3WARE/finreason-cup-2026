from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.irr.after_tax_sale.basic.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"investment costs {N} USD at time 0", text)
    basis = cost  # "that amount remains its tax basis"
    price = grab(r"sold for {N} USD", text)
    tax_rate = grab(r"tax equals {N} percent", text) / 100

    gain = price - basis
    taxable = gain if gain > 0 else Fraction(0)  # strictly positive gain only
    tax = tax_rate * taxable
    after_tax = price - tax
    # one-year holding: (1 + IRR) = after_tax / cost
    irr = (after_tax / cost - 1) * 100
    return {
        "final": irr,
        "slots": {
            "taxable_gain_trace": taxable,
            "gain_tax_trace": tax,
            "after_tax_proceeds_trace": after_tax,
        },
    }
