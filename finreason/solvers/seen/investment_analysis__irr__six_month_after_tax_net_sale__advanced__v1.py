from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.irr.six_month_after_tax_net_sale.advanced.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"investment costs {N} USD at time 0", text)
    basis = cost  # "that amount remains its tax basis"
    price = grab(r"six months later for {N} USD", text)
    sell_cost = grab(r"{N} USD of selling cost", text)
    tax_rate = grab(r"tax equals {N} percent", text) / 100

    net_sale = price - sell_cost
    gain = net_sale - basis
    taxable = gain if gain > 0 else Fraction(0)  # strictly positive net gain only
    after_tax = net_sale - tax_rate * taxable
    multiple = after_tax / cost
    # exact six-month holding period: annualize by squaring the multiple
    irr = (multiple ** 2 - 1) * 100
    return {
        "final": irr,
        "slots": {
            "net_sale_proceeds_trace": net_sale,
            "after_tax_proceeds_trace": after_tax,
            "six_month_gross_multiple_trace": multiple,
        },
    }
