# FINANCE MODEL (h081): two-scenario, two-asset allocation with feasibility interval and endpoint choice.
#
# Inputs
#   C   = total capital
#   p   = downturn probability, (1 - p) = upside probability
#   rB  = Strategy B upside return (gain);   lB = Strategy B downturn loss (fraction of capital lost)
#   a   = positive incremental return of A over B in the upside   -> A upside return  rA = rB + a
#   b   = positive incremental loss of A over B in the downturn   -> A downturn loss  lA = lB + b   (lA < 1)
#   U   = minimum required portfolio ending value in the upside scenario
#   D   = minimum required portfolio ending value in the downturn scenario
#
# Ending values for the FULL capital C placed in one strategy (no fees, leverage, interaction, rebalancing):
#   A_up = C (1 + rA),  A_dn = C (1 - lA)
#   B_up = C (1 + rB),  B_dn = C (1 - lB)
# Portfolio with weight w on A and (1 - w) on B is the linear combination:
#   V_up(w) = w A_up + (1 - w) B_up = B_up + w (A_up - B_up)      (A_up > B_up since a > 0)
#   V_dn(w) = w A_dn + (1 - w) B_dn = B_dn - w (B_dn - A_dn)      (A_dn < B_dn since b > 0)
# Constraints:
#   V_up(w) >= U  ->  w >= w_lo = (U - B_up) / (A_up - B_up)      (increasing in w -> LOWER endpoint)
#   V_dn(w) >= D  ->  w <= w_hi = (B_dn - D) / (B_dn - A_dn)      (decreasing in w -> UPPER endpoint)
# The text asserts the interval is nonempty and strictly inside (0,1); we compute with exact Fractions.
#
# Endpoint choice (exact values, no rounding):
#   EV_A = (1-p) A_up + p A_dn,  EV_B = (1-p) B_up + p B_dn   (probability-weighted ending values)
#   if EV_A > EV_B (strictly): choose upper endpoint w_hi; else (incl. exact tie) choose lower endpoint w_lo.
#
# Final answer: selected exact w expressed in PERCENT (w * 100); framework rounds half up to 2 dp.
#
# Checkpoints (unrounded, framework rounds to 2 dp USD):
#   strategy_a_weighted_upside_checkpoint: Strategy A's probability-weighted upside ending value
#       = (1 - p) * A_up  (the upside-scenario term of A's expected ending value, full capital in A).
#   strategy_b_downturn_checkpoint: Strategy B's ending value in the downturn = B_dn (full capital in B).
#
# Overrides/notes: "loses X" is a fractional loss of capital, ending value = C (1 - X). No rounding is
# applied inside the computation (the text says the displayed percentage is only a reporting approximation).

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h081"


def solve(text: str, q: dict) -> dict:
    C = grab(r"of capital {N} to Strategy A", text)
    p = grab(r"downturn probability is {N}", text)
    rB, lB = grab_all(r"Strategy B earns upside return {N} and loses {N}", text)
    a = grab(r"incremental return {N}", text)
    b = grab(r"incremental loss {N}", text)
    U = grab(r"at least {N} in the upside", text)
    D = grab(r"at least {N} in the downturn", text)

    rA = rB + a
    lA = lB + b

    A_up = C * (1 + rA)
    A_dn = C * (1 - lA)
    B_up = C * (1 + rB)
    B_dn = C * (1 - lB)

    w_lo = (U - B_up) / (A_up - B_up)
    w_hi = (B_dn - D) / (B_dn - A_dn)

    ev_a = (1 - p) * A_up + p * A_dn
    ev_b = (1 - p) * B_up + p * B_dn

    w = w_hi if ev_a > ev_b else w_lo

    return {
        "final": w * 100,
        "slots": {
            "strategy_a_weighted_upside_checkpoint": (1 - p) * A_up,
            "strategy_b_downturn_checkpoint": B_dn,
        },
    }
