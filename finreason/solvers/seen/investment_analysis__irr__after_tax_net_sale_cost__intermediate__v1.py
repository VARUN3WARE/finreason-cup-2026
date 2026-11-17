from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.irr.after_tax_net_sale_cost.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"investment costs {N} USD at time 0", text)
    basis = cost  # "that amount remains its tax basis"
    price = grab(r"sold for {N} USD", text)
    sell_cost = grab(r"Selling cost of {N} USD", text)
    tax_rate = grab(r"tax equals {N} percent", text) / 100

    net_sale = price - sell_cost
    gain = net_sale - basis
    taxable = gain if gain > 0 else Fraction(0)  # strictly positive net gain only
    after_tax = net_sale - tax_rate * taxable
    # one-year holding: (1 + IRR) = after_tax / cost
    irr = (after_tax / cost - 1) * 100
    return {
        "final": irr,
        "slots": {
            "net_sale_proceeds_trace": net_sale,
            "taxable_gain_trace": taxable,
            "after_tax_proceeds_trace": after_tax,
        },
    }
