from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.irr.net_sale_proceeds.basic.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"requires {N} USD at time 0", text)
    sale = grab(r"sold for {N} USD", text)
    sell_cost = grab(r"{N} USD of selling costs", text)
    net = sale - sell_cost
    multiple = net / cost
    irr = multiple - 1  # one-year holding period
    return {
        "final": irr * 100,
        "slots": {
            "net_sale_proceeds_trace": net,
            "gross_return_multiple_trace": multiple,
        },
    }
