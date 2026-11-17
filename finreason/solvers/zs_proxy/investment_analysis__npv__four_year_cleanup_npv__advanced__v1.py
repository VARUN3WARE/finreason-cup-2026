from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.investment_analysis.npv.four_year_cleanup_npv.advanced.v1"


def solve(text: str, q: dict) -> dict:
    i0 = grab(r"costs USD {N} now", text)
    cfs = grab_all(
        r"pays USD {N}, USD {N}, USD {N},? and USD {N} at the ends of years one through four", text
    )
    cleanup = grab(r"cleanup outflow of USD {N}", text)
    r = grab(r"discount rate is {N} percent", text) / 100
    gross = sum((cf / (1 + r) ** t for t, cf in enumerate(cfs, start=1)), Fraction(0))
    # Cleanup is described as an outflow (cost) that is subtracted; its PV is reported as a positive cost.
    pv_cleanup = cleanup / (1 + r) ** 4
    after_initial = gross - i0
    return {
        "final": after_initial - pv_cleanup,
        "slots": {
            "gross_pv_trace": gross,
            "pv_cleanup_trace": pv_cleanup,
            "after_initial_trace": after_initial,
        },
    }
