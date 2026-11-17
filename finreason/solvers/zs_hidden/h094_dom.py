# FINANCE MODEL
# Cash flows: -I at t=0, +C1 at end of year 1, +C2 at end of year 2.
# Annual effective trial rate r0 (given as a decimal, 0.1 = 10%).
#   NPV(r)  = -I + C1/(1+r) + C2/(1+r)^2
#   NPV'(r) = -C1/(1+r)^2 - 2*C2/(1+r)^3   (always negative for positive cash flows)
# Newton-Raphson step: r1 = r0 - NPV(r0)/NPV'(r0) = r0 + NPV(r0)/|NPV'(r0)|.
#   The text says to use the positive magnitude of the derivative; with NPV > 0 the
#   update moves upward, which is consistent with the standard Newton step.
# Exactly one update, no iteration. Everything exact (Fractions), no rounding inside.
# Final answer: r1 expressed in percent (r1 * 100), rounded by the framework to 2 dp half-up.
# Checkpoint (year_two_present_value_checkpoint): PV of year-2 cash flow at the TRIAL rate r0,
#   = C2/(1+r0)^2, in USD (unit as given, no scaling).
# Overrides: none.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h094"


def solve(text: str, q: dict) -> dict:
    i0 = grab(r"initial outlay of {N} at time 0", text)
    c1 = grab(r"pays {N} at the end of year 1", text)
    c2 = grab(r"pays {N} at the end of year 2", text)
    r0 = grab(r"trial rate {N}", text)

    d1 = 1 + r0
    pv1 = c1 / d1
    pv2 = c2 / d1 ** 2
    npv = -i0 + pv1 + pv2
    dnpv_mag = c1 / d1 ** 2 + 2 * c2 / d1 ** 3  # |NPV'(r0)|
    r1 = r0 + npv / dnpv_mag

    slots = {"year_two_present_value_checkpoint": pv2}
    return {"final": r1 * 100, "slots": slots}
