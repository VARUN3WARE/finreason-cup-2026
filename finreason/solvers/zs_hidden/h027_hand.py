from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h027"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"forecast net income is {N}", text)
    reserve = grab(r"mandatory reserve is {N}", text)
    de = ni - reserve

    payout = grab(r"distributable earnings times {N}", text)
    t_floor = grab(r"target-payout policy.*?retained distributable earnings of at least {N}", text)

    d0 = grab(r"prior total cash dividend {N}", text)
    g = grab(r"per-period rate {N}", text)
    s_floor = grab(r"stable-growth policy starts.*?retained distributable earnings of at least {N}", text)

    cap = grab(r"proposed dividend does not exceed {N}", text)

    multiple = 1 + g
    t_div = de * payout
    s_div = d0 * multiple ** 3

    t_ok = t_div <= cap and (de - t_div) >= t_floor
    s_ok = s_div <= cap and (de - s_div) >= s_floor

    if t_ok and s_ok:
        final = "target_payout" if t_div >= s_div else "stable_growth"
    elif t_ok:
        final = "target_payout"
    elif s_ok:
        final = "stable_growth"
    else:
        final = "no_feasible_policy"

    return {"final": final, "slots": {"one_period_growth_multiple_checkpoint": multiple}}
