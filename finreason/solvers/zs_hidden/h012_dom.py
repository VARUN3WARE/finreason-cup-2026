# FINANCE MODEL (h012): whale-transfer concentration check (AML-style monitoring).
#
# Inputs: current transfer c, prior transfers p1, p2, rolling-window whale threshold T,
#   single-transfer haircut ratio h, total activity A over the monitoring horizon
#   (includes the three transfers but may also include other flows), concentration cut-off k.
#
# 1. Retained fraction  r = 1 - h                      (checkpoint, ratio, 6dp half-up)
# 2. Haircut-adjusted single-transfer threshold  S = T * r
# 3. Concentration  q = c / A   (A = stated TOTAL ACTIVITY, not the sum of the three transfers)
# 4. Branch (exact Fraction comparison, inclusive):
#       q >= k  -> final = c - S                       (current transfer excess over adjusted threshold)
#       else    -> final = (c + p1 + p2) - T           (THREE-TRANSFER total's excess over UNADJUSTED
#                                                       rolling threshold)
#    Note: "three-transfer total" = c + p1 + p2 (sum of the three named transfers); this is
#    distinct from "total activity" A used only as the concentration denominator.
#    Excess is a signed difference (no floor at zero stated); sign preserved.
# 5. Final rounded half-up to 2dp by the framework; everything here is unrounded exact.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h012"


def solve(text: str, q: dict) -> dict:
    c = grab(r"current transfer of {N} USD", text)
    p1, p2 = grab_all(r"prior transfers of {N} USD and {N} USD", text)
    T = grab(r"rolling-window whale threshold is {N} USD", text)
    h = grab(r"haircut ratio {N}", text)
    A = grab(r"including all three transfers, is {N} USD", text)
    k = grab(r"If it is at least {N}", text)

    retained = 1 - h
    single_thr = T * retained
    conc = c / A
    if conc >= k:
        final = c - single_thr
    else:
        final = (c + p1 + p2) - T
    return {"final": final, "slots": {"single_threshold_retention_checkpoint": retained}}
