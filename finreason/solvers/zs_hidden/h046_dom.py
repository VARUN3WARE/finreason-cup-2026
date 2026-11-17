# MODEL (h046): three-year retirement bridge with a growing withdrawal schedule.
#   P  = opening capital (the amount the saver "enters ... with")
#   r  = annual earning rate on the remaining balance (the "earns {r} annually" figure), compounding yearly
#   g  = growth rate of the withdrawal schedule (the "W times one plus {g}" figure); it is a SEPARATE
#        parameter from r (it differs from r in some instances, so it must be parsed on its own)
#   R  = required reserve remaining immediately after the third withdrawal
#   Withdrawals at year-ends: W (t=1), W(1+g) (t=2), W(1+g)^2 (t=3).
#   Balance recursion: B_t = B_{t-1}(1+r) - w_t, B_0 = P, and B_3 = R.
#   => B_3 = P(1+r)^3 - W[(1+r)^2 + (1+g)(1+r) + (1+g)^2] = R
#   => W = (P(1+r)^3 - R) / ((1+r)^2 + (1+r)(1+g) + (1+g)^2)       (exact, unrounded)
#   Checkpoint "gross two-year value of the opening capital before withdrawals" = P(1+r)^2
#   (opening capital compounded two years, no withdrawals deducted).
#   Rates are given as decimals (0.04 = 4%), NOT percents. Everything in USD; no rounding inside the calculation.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h046"


def solve(text: str, q: dict) -> dict:
    P = grab(r"enters a three-year retirement bridge with {N}\.", text)
    r = grab(r"balance earns {N} annually", text)
    g = grab(r"W times one plus {N} after year 2", text)
    R = grab(r"Immediately after the third withdrawal, {N} must remain", text)

    a = 1 + r
    b = 1 + g
    denom = a ** 2 + a * b + b ** 2
    W = (P * a ** 3 - R) / denom
    gross2 = P * a ** 2
    return {"final": W, "slots": {"two_year_gross_capital_checkpoint": gross2}}
