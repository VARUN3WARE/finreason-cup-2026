from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.irr.bond_coupon_reinvestment.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    price = grab(r"investor pays {N} USD at time 0", text)
    par = grab(r"one-year {N} USD par bond", text)
    coupon_rate = grab(r"Its {N} percent nominal annual coupon", text) / 100
    reinv_rate = grab(r"simple annual rate of {N} percent", text) / 100

    coupon = par * coupon_rate / 2
    # first coupon reinvested at simple interest for the remaining half year
    reinvested = coupon * (1 + reinv_rate * Fraction(1, 2))
    terminal = par + coupon + reinvested
    irr = (terminal / price - 1) * 100
    return {
        "final": irr,
        "slots": {
            "semiannual_coupon_trace": coupon,
            "reinvested_first_coupon_trace": reinvested,
            "terminal_cash_trace": terminal,
        },
    }
