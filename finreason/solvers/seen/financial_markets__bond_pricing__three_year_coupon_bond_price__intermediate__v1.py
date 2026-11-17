from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.bond_pricing.three_year_coupon_bond_price.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    face = grab(r"face value USD {N}", text)
    rate = grab(r"annual coupon equal to {N} percent of face value", text)
    y = grab(r"effective annual yield of {N} percent", text) / 100
    coupon = face * rate / 100
    terminal = coupon + face
    g = 1 + y
    pv_terminal = terminal / g ** 3
    price = coupon / g + coupon / g ** 2 + pv_terminal
    return {
        "final": price,
        "slots": {
            "annual_coupon_trace": coupon,
            "terminal_cash_flow_trace": terminal,
            "pv_terminal_trace": pv_terminal,
        },
    }
