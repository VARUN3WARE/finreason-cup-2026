"""h027 -- target-payout vs three-period stable-growth dividend policy (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h027"


def solve(text: str, q: dict) -> dict:
    # "forecast net income is {NI} and the mandatory reserve is {R}"
    net_income = grab(r"forecast net income is {N}", text)
    reserve = grab(r"mandatory reserve is {N}", text)
    # "distributable earnings equal forecast net income minus the reserve"
    distributable = net_income - reserve

    # Target-payout: "terminal total dividend equal to distributable earnings times {p}"
    payout = grab(r"distributable earnings times {N}", text)
    target_div = distributable * payout
    # "...and requires retained distributable earnings of at least {floor_t}"
    target_floor = grab(
        r"target-payout policy proposes.*?requires retained distributable earnings of at least {N}", text
    )

    # Stable-growth: "starts from prior total cash dividend {D0} ... per-period rate {g}"
    prior_div = grab(r"prior total cash dividend {N}", text)
    g = grab(r"per-period rate {N}", text)
    # "one-period growth multiple" = 1 + g
    multiple = 1 + g
    # "terminal total dividend equals the prior total cash dividend times (1 + the growth rate)^3"
    stable_div = prior_div * multiple ** 3
    # "it requires retained distributable earnings of at least {floor_s}"
    stable_floor = grab(
        r"stable-growth policy starts.*?requires retained distributable earnings of at least {N}", text
    )

    # "a policy qualifies only if its proposed dividend does not exceed {cap}
    #  and its policy-specific retained-earnings floor is met"
    cap = grab(r"proposed dividend does not exceed {N}", text)

    def qualifies(div: Fraction, floor: Fraction) -> bool:
        retained = distributable - div
        return div <= cap and retained >= floor

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
