from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h016"


def solve(text: str, q: dict) -> dict:
    c0 = grab(r"receives {N} USD at the start", text)
    n = grab(r"each lasting {N} whole annual compounding periods", text)
    assert n.denominator == 1
    n = int(n)
    r1 = grab(r"first-phase annual rate ratio is {N}", text)
    r2 = grab(r"second-phase rate ratio is {N}", text)
    c1 = grab(r"and {N} USD is added at the phase boundary", text)

    g1 = 1 + r1
    g2 = 1 + r2
    a1 = g1 ** n                      # actual first-phase compound factor
    a2 = g2 ** n                      # actual second-phase compound factor
    gm = (g1 + g2) / 2                # arithmetic mean of annual growth factors
    s = gm ** n                       # smoothed one-phase compound factor

    # initial contribution at t=0 grows over both phases; boundary contribution grows over phase 2 only
    drag = c0 * s * s - c0 * a1 * a2  # smoothed TV minus actual TV
    uplift = c1 * a2 - c1 * s         # actual TV minus smoothed TV
    total = c0 + c1                   # nominal undiscounted contributed cash

    final = (drag / total) * (uplift / total) * 100
    return {
        "final": Fraction(final),
        "slots": {
            "first_phase_growth_checkpoint": Fraction(a1),
            "smoothed_phase_growth_checkpoint": Fraction(s),
        },
    }
