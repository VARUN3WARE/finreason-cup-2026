from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h027"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"forecast net income is {N}", text)
    reserve = grab(r"mandatory reserve is {N}", text)
    de = ni - reserve  # distributable earnings

    tp_ratio = grab(r"distributable earnings times {N}", text)
    tp_floor = grab(r"target-payout policy.*?retained distributable earnings of at least {N}", text)

    prior = grab(r"prior total cash dividend {N}", text)
    g = grab(r"per-period rate {N}", text)
    sg_floor = grab(r"stable-growth policy starts.*?retained distributable earnings of at least {N}", text)

    cap = grab(r"proposed dividend does not exceed {N}", text)

    tp_div = de * tp_ratio
    multiple = 1 + g                 # one-period growth multiple
    sg_div = prior * multiple ** 3   # compounded exactly three periods

    tp_ok = tp_div <= cap and (de - tp_div) >= tp_floor
    sg_ok = sg_div <= cap and (de - sg_div) >= sg_floor

    if tp_ok and sg_ok:
        final = "target_payout" if tp_div >= sg_div else "stable_growth"
    elif tp_ok:
        final = "target_payout"
    elif sg_ok:
        final = "stable_growth"
    else:
        final = "no_feasible_policy"

    return {"final": final, "slots": {"one_period_growth_multiple_checkpoint": Fraction(multiple)}}
