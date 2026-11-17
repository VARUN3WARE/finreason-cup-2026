# FINANCE MODEL (h016)
# An account gets an initial contribution C0 at time 0 and a boundary contribution C1 at the end of phase 1
# (= start of phase 2). Each phase lasts n whole annual compounding periods; phase rates r1 (phase 1) and
# r2 (phase 2, strictly higher). Annual growth factors g1 = 1 + r1, g2 = 1 + r2 ("rate ratio" = decimal rate).
#   Actual terminal values (annual compounding, integer exponents, exact):
#       initial  : C0 * g1^n * g2^n
#       boundary : C1 * g2^n               (boundary cash only experiences phase 2)
#   Smoothed counterfactual: gm = (g1 + g2) / 2 (arithmetic mean of GROWTH FACTORS, not of rates) used in both
#   phases, contribution dates preserved:
#       initial  : C0 * gm^n * gm^n = C0 * gm^(2n)
#       boundary : C1 * gm^n
#   drag   = smoothed_initial  - actual_initial     (smoothed minus actual, as worded; no clamping)
#   uplift = actual_boundary   - smoothed_boundary  (actual minus smoothed, as worded; no clamping)
#   Each is divided by nominal undiscounted contributed cash S = C0 + C1 (decimal ratios, NOT percent),
#   the two ratios are multiplied ONCE, and the product x 100 is the final answer in percent.
# Checkpoints:
#   1. actual first-phase compound growth factor = g1^n  (multiple)
#   2. one-phase compound growth factor under the smoothed counterfactual = gm^n  (multiple)
# Overrides: none. Everything exact Fractions; no intermediate rounding.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h016"


def solve(text: str, q: dict) -> dict:
    c0 = grab(r"receives {N} USD at the start", text)
    n = grab(r"each lasting {N} whole annual", text)
    r1 = grab(r"first-phase annual rate ratio is {N}", text)
    r2 = grab(r"second-phase rate ratio is {N}", text)
    c1 = grab(r"and {N} USD is added at the phase boundary", text)
    n = int(n)

    g1 = 1 + r1
    g2 = 1 + r2
    gm = (g1 + g2) / 2

    act_init = c0 * g1 ** n * g2 ** n
    act_bound = c1 * g2 ** n
    sm_init = c0 * gm ** n * gm ** n
    sm_bound = c1 * gm ** n

    drag = sm_init - act_init
    uplift = act_bound - sm_bound
    total = c0 + c1

    final = (drag / total) * (uplift / total) * 100

    return {
        "final": final,
        "slots": {
            "first_phase_growth_checkpoint": g1 ** n,
            "smoothed_phase_growth_checkpoint": gm ** n,
        },
    }
