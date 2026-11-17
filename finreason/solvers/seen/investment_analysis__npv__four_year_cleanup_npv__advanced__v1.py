from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.investment_analysis.npv.four_year_cleanup_npv.advanced.v1"


def solve(text: str, q: dict) -> dict:
    i0 = grab(r"costs USD {N} now", text)
    flows = grab_all(
        r"pays USD {N}, USD {N}, USD {N},? and USD {N} at the ends of years one through four", text
    )
    cleanup = grab(r"cleanup outflow of USD {N}", text)
    r = grab(r"discount rate is {N} percent", text) / 100
    g = 1 + r
    gross = sum((cf / g**t for t, cf in enumerate(flows, start=1)), Fraction(0))
    pv_cleanup = cleanup / g**4
    after_initial = gross - i0
    return {
        "final": after_initial - pv_cleanup,
        "slots": {
            "gross_pv_trace": gross,
            "pv_cleanup_trace": pv_cleanup,
            "after_initial_trace": after_initial,
        },
    }
