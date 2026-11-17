from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h027"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"forecast net income is {N}", text)
    reserve = grab(r"mandatory reserve is {N}", text)
    # distributable earnings = forecast net income - reserve
    dist = ni - reserve

    payout = grab(r"distributable earnings times {N}", text)
    tp_floor = grab(r"requires retained distributable earnings of at least {N}", text)
    prior = grab(r"prior total cash dividend {N}", text)
    rate = grab(r"per-period rate {N}", text)
    # second "retained distributable earnings of at least" belongs to the stable-growth policy
    sg_floor = grab(r"stable-growth policy starts.*?requires retained distributable earnings of at least {N}", text)
    cap = grab(r"does not exceed {N}", text)

    # one-period growth multiple (exact, unrounded); compounded exactly three periods
    mult = 1 + rate
    tp_div = dist * payout
    sg_div = prior * mult ** 3

    # retained distributable earnings = distributable earnings - proposed dividend
    tp_ok = tp_div <= cap and (dist - tp_div) >= tp_floor
    sg_ok = sg_div <= cap and (dist - sg_div) >= sg_floor

    if tp_ok and sg_ok:
        final = "target_payout" if tp_div >= sg_div else "stable_growth"
    elif tp_ok:
        final = "target_payout"
    elif sg_ok:
        final = "stable_growth"
    else:
        final = "no_feasible_policy"

    return {"final": final, "slots": {"one_period_growth_multiple_checkpoint": mult}}
