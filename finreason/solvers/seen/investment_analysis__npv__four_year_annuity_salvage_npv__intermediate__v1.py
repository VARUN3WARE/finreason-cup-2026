from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.npv.four_year_annuity_salvage_npv.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    i0 = grab(r"costs USD {N} now", text)
    cf = grab(r"generates USD {N} at each year-end for four years", text)
    salvage = grab(r"USD {N} of salvage at the end of year four", text)
    r = grab(r"discount rate of {N} percent", text) / 100
    g = 1 + r
    year_four = cf + salvage
    pv4 = year_four / g**4
    total = cf / g + cf / g**2 + cf / g**3 + pv4
    return {
        "final": total - i0,
        "slots": {
            "year_four_total_trace": year_four,
            "pv_year_four_trace": pv4,
            "total_pv_trace": total,
        },
    }
