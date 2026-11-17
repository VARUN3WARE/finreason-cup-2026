"""h094 -- one Newton-Raphson IRR update on a two-year cash-flow stream (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h094"


def solve(text: str, q: dict) -> dict:
    # "An investment requires an initial outlay of C0 at time 0,"
    c0 = grab(r"initial outlay of {N} at time 0", text)
    # "pays CF1 at the end of year 1,"
    cf1 = grab(r"pays {N} at the end of year 1", text)
    # "and pays CF2 at the end of year 2."
    cf2 = grab(r"pays {N} at the end of year 2", text)
    # "Starting from the annual effective trial rate r0,"
    r0 = grab(r"annual effective trial rate {N}", text)

    # "evaluate the exact two-year NPV"
    v = 1 / (1 + r0)
    pv1 = cf1 * v
    pv2 = cf2 * v ** 2          # checkpoint: PV of the year-2 cash flow at the trial rate
    npv = -c0 + pv1 + pv2

    # NPV derivative d/dr: -CF1/(1+r)^2 - 2*CF2/(1+r)^3 ; use its positive magnitude
    dnpv = -cf1 * v ** 2 - 2 * cf2 * v ** 3
    mag = abs(dnpv)

    # "perform exactly one Newton-Raphson update using the positive magnitude of the NPV derivative"
    # Positive NPV => update moves upward: r1 = r0 + NPV / |NPV'|  (identical to r0 - NPV/NPV')
    r1 = r0 + npv / mag

    # "Report the updated trial rate as an annual percentage."
    final = r1 * 100

    return {
        "final": final,
        "slots": {"year_two_present_value_checkpoint": pv2},
    }
