from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.irr.six_month_after_tax_net_sale.advanced.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"costs {N} USD at time 0", text)
    sale = grab(r"later for {N} USD", text)
    sell_cost = grab(r"{N} USD of selling cost", text)
    tax_rate = grab(r"tax equals {N} percent", text) / 100
    basis = cost  # "that amount remains its tax basis"
    net = sale - sell_cost
    gain = net - basis
    taxable = gain if gain > 0 else Fraction(0)  # tax only on strictly positive net gain
    after_tax = net - tax_rate * taxable
    multiple = after_tax / cost  # six-month gross multiple
    irr = multiple ** 2 - 1  # stated rule: square the six-month multiple
    return {
        "final": irr * 100,
        "slots": {
            "net_sale_proceeds_trace": net,
            "after_tax_proceeds_trace": after_tax,
            "six_month_gross_multiple_trace": multiple,
        },
    }
