# FINANCE MODEL (h065): time-weighted return (TWR, chain-linked at the contribution instant) minus Modified Dietz.
#
# Inputs:  V0   = beginning value
#          C    = contribution, added at fraction t of the period (t = elapsed fraction)
#          Vpre = account value immediately BEFORE the contribution (at time t)
#          Vend = ending value AFTER the terminal distribution (excludes the distribution)
#          D    = terminal cash distribution paid at the period end (value that left the account at t=1)
#
# Total ending value attributable to the investor (pre-distribution) = Vend + D. The distribution is a payout
# at the very end; it is NOT lost return, so it is added back to the ending value (total-return convention).
# For Modified Dietz, treating D as an end-of-period outflow (weight 0) gives the identical gain
#   Vend - V0 - (C - D) = (Vend + D) - V0 - C, so both views agree.
#
# Subperiod 1 (pre-contribution):   r1 = Vpre / V0 - 1                          (no flows, no valuation jump)
# Post-contribution starting value: Vpost = Vpre + C                            (no other flows/valuation changes at t)
# Subperiod 2 (post-contribution):  r2 = (Vend + D) / (Vpost) - 1
# TWR = (1 + r1)(1 + r2) - 1
#
# Modified Dietz: MD = (EMV - BMV - C) / (BMV + w*C), with EMV = Vend + D (distribution included),
#                 w = remaining-period weight of the contribution = 1 - t.
#
# Answer = (TWR - MD) * 100 percentage points, signed. Checkpoint = r1 as a plain ratio (unrounded exact).
# Nothing is rounded inside the computation.

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h065"


def solve(text: str, q: dict) -> dict:
    v0 = grab(r"begins a measurement period at value {N}", text)
    c = grab(r"a contribution of {N} is added", text)
    t = grab(r"after {N} of the period has elapsed", text)
    vpre = grab(r"the account value is {N}\.", text)
    vend = grab(r"post-distribution account value is {N}", text)
    d = grab(r"terminal cash distribution of {N} is paid", text)

    r1 = vpre / v0 - 1
    vpost = vpre + c
    emv = vend + d
    r2 = emv / vpost - 1
    twr = (1 + r1) * (1 + r2) - 1

    w = 1 - t
    md = (emv - v0 - c) / (v0 + w * c)

    final = (twr - md) * 100
    return {"final": final, "slots": {"period_one_return_checkpoint": r1}}
