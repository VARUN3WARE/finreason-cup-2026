from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.bond_pricing.two_year_par_bond_ytm.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    face = grab(r"face value USD {N}", text)
    rate = grab(r"at a rate of {N} percent of face value", text)
    coupon = face * rate / 100
    ytm = coupon / face  # par bond: YTM = annual coupon / face (price = face)
    return {
        "final": ytm * 100,
        "slots": {"annual_coupon_trace": coupon, "ytm_ratio_trace": ytm},
    }
