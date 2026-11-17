from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h027"


def solve(text: str, q: dict) -> dict:
    # Common horizon inputs (USD millions).
    net_income = grab(r"forecast net income is {N}", text)
    reserve = grab(r"mandatory reserve is {N}", text)
    distributable = net_income - reserve  # "distributable earnings equal forecast net income minus the reserve"

    # Target-payout policy: dividend = distributable * payout ratio; floor on retained distributable earnings.
    payout_ratio = grab(r"distributable earnings times {N}", text)
    target_floor = grab(
        r"target-payout policy proposes.*?requires retained distributable earnings of at least {N}", text
    )
    target_div = distributable * payout_ratio

    # Stable-growth policy: prior dividend compounded for exactly three periods at the per-period rate.
    prior_div = grab(r"prior total cash dividend {N}", text)
    rate = grab(r"per-period rate {N}", text)
    stable_floor = grab(
        r"stable-growth policy starts.*?it requires retained distributable earnings of at least {N}", text
    )
    multiple = 1 + rate  # one-period growth multiple (the checkpoint)
    stable_div = prior_div * multiple ** 3

    # Qualification: proposed dividend must not exceed the cap (non-strict) and the
    # policy-specific retained floor must be met (non-strict), where retained
    # distributable earnings = distributable earnings - proposed dividend.
    cap = grab(r"proposed dividend does not exceed {N}", text)

    def qualifies(div: Fraction, floor: Fraction) -> bool:
        return div <= cap and (distributable - div) >= floor

    t_ok = qualifies(target_div, target_floor)
    s_ok = qualifies(stable_div, stable_floor)

    if t_ok and s_ok:
        final = "target_payout" if target_div >= stable_div else "stable_growth"
    elif t_ok:
        final = "target_payout"
    elif s_ok:
        final = "stable_growth"
    else:
        final = "no_feasible_policy"

    return {"final": final, "slots": {"one_period_growth_multiple_checkpoint": multiple}}
