# FINANCE MODEL
# -------------
# Two dividend policies are compared at a common terminal date (end of a 3-period horizon).
#   Distributable earnings   DE = forecast net income - mandatory reserve.
#   Target-payout policy     terminal dividend D_T = DE * payout_ratio.
#   Stable-growth policy     terminal dividend D_S = D0 * (1 + g)^3   (D0 = prior total cash dividend,
#                            g = per-period growth rate, compounded exactly 3 periods; text-stated).
#   Retained distributable earnings (per policy) = DE - proposed terminal dividend.
#   Policy-specific floor: retained >= floor_policy  ("at least" -> non-strict).
#   Cap: proposed dividend <= cap ("does not exceed" -> non-strict), common to both policies.
#   Qualifies  <=>  dividend <= cap  AND  retained >= its own floor.
# Decision:
#   both qualify -> "target_payout" if D_T >= D_S (tie goes to target_payout) else "stable_growth"
#   exactly one qualifies -> that one
#   none -> "no_feasible_policy"
# Checkpoint: one-period growth multiple used by the stable policy = 1 + g (a plain multiple,
#   unrounded exact Fraction; the framework rounds to 6 dp half-up).
# No overrides of standard conventions; all monetary amounts in USD millions (consistent units).
# Everything exact in Fractions (no rounding inside the computation).

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h027"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"forecast net income is {N}", text)
    reserve = grab(r"mandatory reserve is {N}", text)
    de = ni - reserve

    payout = grab(r"distributable earnings times {N}", text)
    floor_t = grab(r"requires retained distributable earnings of at least {N}", text)  # first = target policy
    d0 = grab(r"prior total cash dividend {N}", text)
    g = grab(r"per-period rate {N}", text)
    # second "requires retained ... of at least" belongs to the stable-growth policy
    floor_s = after(text, "requires retained distributable earnings of at least", 1)
    cap = grab(r"does not exceed {N}", text)

    mult = 1 + g
    d_t = de * payout
    d_s = d0 * mult ** 3

    ret_t = de - d_t
    ret_s = de - d_s

    ok_t = (d_t <= cap) and (ret_t >= floor_t)
    ok_s = (d_s <= cap) and (ret_s >= floor_s)

    if ok_t and ok_s:
        final = "target_payout" if d_t >= d_s else "stable_growth"
    elif ok_t:
        final = "target_payout"
    elif ok_s:
        final = "stable_growth"
    else:
        final = "no_feasible_policy"

    return {"final": final, "slots": {"one_period_growth_multiple_checkpoint": mult}}
