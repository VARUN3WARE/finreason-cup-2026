# FINANCE MODEL
# Net book value NBV0 = original cost - accumulated depreciation (USD millions).
# Each scenario revises the residual value R; the depreciable balance above residual is
#   B0 = NBV0 - R   (residual itself is never depreciated).
# Declining-balance on the balance above residual, per-subperiod ratio r, applied n = 3 times
# (three equal sequential subperiods, ratio applies again each time to the remaining balance above residual):
#   retention factor per subperiod  k = 1 - r
#   B_n = B0 * k**n            (remaining depreciable balance above residual after 3 stages)
#   cumulative 3-stage depreciation D_n = B0 - B_n = B0 * (1 - k**n)
# Qualification: D_n <= max-depreciation threshold (at most) AND B_n >= min-remaining threshold (at least).
# Winner: qualifying scenario with lower exact D_n; exact tie -> Scenario A; none qualifies -> "Neither scenario".
# Checkpoint a_one_stage_retention_factor_checkpoint = Scenario A's k = 1 - r_A (plain ratio).
# Overrides: none. Cumulative depreciation counts only the three new stages (not the existing accumulated 59 etc.).
from fractions import Fraction
from finreason.nums import grab, grab_all, F

TEMPLATE_ID = "h072"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"original cost {N}", text)
    acc = grab(r"accumulated depreciation of {N}", text)
    nbv = cost - acc

    rA, ratioA = grab_all(r"Scenario A revises residual value to {N} and applies per-subperiod depreciation ratio {N}", text)
    rB, ratioB = grab_all(r"Scenario B uses {N} and {N}", text)

    n = 3  # "exactly three equal sequential subperiods"
    max_dep = grab(r"cumulative three-stage depreciation is at most {N}", text)
    min_rem = grab(r"remaining depreciable balance above residual is at least {N}", text)

    def run(resid, ratio):
        b0 = nbv - resid
        k = 1 - ratio
        rem = b0 * k ** n
        dep = b0 - rem
        return k, dep, rem

    kA, depA, remA = run(rA, ratioA)
    kB, depB, remB = run(rB, ratioB)

    qA = depA <= max_dep and remA >= min_rem
    qB = depB <= max_dep and remB >= min_rem

    if qA and qB:
        final = "Scenario A" if depA <= depB else "Scenario B"
    elif qA:
        final = "Scenario A"
    elif qB:
        final = "Scenario B"
    else:
        final = "Neither scenario"

    return {"final": final, "slots": {"a_one_stage_retention_factor_checkpoint": kA}}
