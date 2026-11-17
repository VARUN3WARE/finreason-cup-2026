from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.npv.single_year_npv.basic.v1"


def solve(text: str, q: dict) -> dict:
    i0 = grab(r"costs USD {N} at time zero", text)
    cf1 = grab(r"pays USD {N} at the end of year one", text)
    r = grab(r"discount rate is {N} percent", text) / 100
    factor = 1 + r
    pv1 = cf1 / factor
    return {
        "final": pv1 - i0,
        "slots": {"present_value_trace": pv1, "discount_factor_trace": factor},
    }
