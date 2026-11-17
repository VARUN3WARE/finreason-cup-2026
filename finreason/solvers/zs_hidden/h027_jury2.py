from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h027"


def solve(text: str, q: dict) -> dict:
    net_income = grab(r"forecast net income is {N}", text)
    reserve = grab(r"mandatory reserve is {N}", text)
    payout_ratio = grab(r"distributable earnings times {N}", text)
    tp_floor = grab(r"target-payout policy.*?retained distributable earnings of at least {N}", text)
    prior_div = grab(r"prior total cash dividend {N}", text)
    g = grab(r"per-period rate {N}", text)
    sg_floor = grab(r"stable-growth policy starts.*?retained distributable earnings of at least {N}", text)
    cap = grab(r"proposed dividend does not exceed {N}", text)

    distributable = net_income - reserve

    tp_div = distributable * payout_ratio
    tp_retained = distributable - tp_div
    tp_ok = tp_div <= cap and tp_retained >= tp_floor

    multiple = 1 + g                      # one-period growth multiple
    sg_div = prior_div * multiple ** 3    # exactly three periods of compounding
    sg_retained = distributable - sg_div
    sg_ok = sg_div <= cap and sg_retained >= sg_floor

    if tp_ok and sg_ok:
        final = "target_payout" if tp_div >= sg_div else "stable_growth"
    elif tp_ok:
        final = "target_payout"
    elif sg_ok:
        final = "stable_growth"
    else:
        final = "no_feasible_policy"

    return {"final": final, "slots": {"one_period_growth_multiple_checkpoint": multiple}}
