from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.npv.two_year_npv.basic.v1"


def solve(text: str, q: dict) -> dict:
    i0 = grab(r"costs USD {N} at time zero", text)
    cf1 = grab(r"pays USD {N} at the end of year one", text)
    cf2 = grab(r"USD {N} at the end of year two", text)
    r = grab(r"discount rate is {N} percent", text) / 100
    pv1 = cf1 / (1 + r)
    pv2 = cf2 / (1 + r) ** 2
    total = pv1 + pv2
    return {
        "final": total - i0,
        "slots": {"pv_one_trace": pv1, "pv_two_trace": pv2, "total_pv_trace": total},
    }
