"""h094: one Newton-Raphson step on a two-year NPV from a trial rate."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h094"


def solve(text: str, q: dict) -> dict:
    c0 = grab(r"initial outlay of {N}", text)
    c1 = grab(r"pays {N} at the end of year 1", text)
    c2 = grab(r"pays {N} at the end of year 2", text)
    r0 = grab(r"trial rate {N}", text)

    g = 1 + r0
    pv1 = c1 / g
    pv2 = c2 / g ** 2
    npv = -c0 + pv1 + pv2
    # NPV'(r) = -c1/(1+r)^2 - 2 c2/(1+r)^3; use its positive magnitude.
    dmag = abs(-c1 / g ** 2 - 2 * c2 / g ** 3)
    r1 = r0 + npv / dmag

    return {
        "final": r1 * 100,
        "slots": {"year_two_present_value_checkpoint": pv2},
    }
