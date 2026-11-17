from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.irr.bond_coupon_reinvestment.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    price = grab(r"pays {N} USD at time 0", text)
    par = grab(r"one-year {N} USD par bond", text)
    coupon_rate = grab(r"Its {N} percent nominal annual coupon", text) / 100
    reinv_rate = grab(r"simple annual rate of {N} percent", text) / 100
    coupon = par * coupon_rate / 2  # two equal semiannual coupons
    reinvested_first = coupon * (1 + reinv_rate * Fraction(1, 2))  # simple interest for six months
    terminal = par + coupon + reinvested_first
    irr = terminal / price - 1  # one-year horizon: effective annual
    return {
        "final": irr * 100,
        "slots": {
            "semiannual_coupon_trace": coupon,
            "reinvested_first_coupon_trace": reinvested_first,
            "terminal_cash_trace": terminal,
        },
    }
