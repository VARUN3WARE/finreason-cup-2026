from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.irr.after_tax_net_sale_cost.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"costs {N} USD at time 0", text)
    sale = grab(r"sold for {N} USD", text)
    sell_cost = grab(r"[Ss]elling cost of {N} USD", text)
    tax_rate = grab(r"tax equals {N} percent", text) / 100
    basis = cost  # "that amount remains its tax basis"
    net = sale - sell_cost
    gain = net - basis
    taxable = gain if gain > 0 else Fraction(0)  # tax only on strictly positive net gain
    tax = tax_rate * taxable
    after_tax = net - tax
    irr = after_tax / cost - 1  # one-year holding period
    return {
        "final": irr * 100,
        "slots": {
            "net_sale_proceeds_trace": net,
            "taxable_gain_trace": taxable,
            "after_tax_proceeds_trace": after_tax,
        },
    }
