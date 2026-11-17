from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h027"

# Target-payout vs three-period stable-growth dividend policy (juror #5).
#
# Sentence-by-sentence rules:
#   * distributable earnings DE = forecast net income - mandatory reserve
#   * target-payout dividend  D_t = DE * payout_ratio
#   * stable-growth dividend  D_s = prior_dividend * (1 + g)^3   (exact integer power, no rounding)
#   * "retained distributable earnings" of a policy = DE - that policy's proposed dividend
#     (the part of *distributable* earnings not paid out; the reserve is already excluded)
#   * a policy qualifies iff  dividend <= cap  (non-strict: "does not exceed")
#                        and  DE - dividend >= its own floor (non-strict: "floor is met")
#   * both qualify  -> target_payout if D_t >= D_s (tie -> target_payout) else stable_growth
#   * one qualifies -> that one;  none -> no_feasible_policy
#   * checkpoint = one-period growth multiple (1 + g), unrounded.


def solve(text: str, q: dict) -> dict:
    net_income = grab(r"forecast net income is {N}", text)
    reserve = grab(r"mandatory reserve is {N}", text)
    payout_ratio = grab(r"distributable earnings times {N}", text)
    target_floor = grab(
        r"times \S+ and requires retained distributable earnings of at least {N}", text
    )
    prior_div = grab(r"prior total cash dividend {N}", text)
    rate = grab(r"per-period rate {N}", text)
    stable_floor = grab(
        r"\^3; it requires retained distributable earnings of at least {N}", text
    )
    cap = grab(r"proposed dividend does not exceed {N}", text)

    de = net_income - reserve
    multiple = 1 + rate  # one-period growth multiple used by the stable policy

    div_target = de * payout_ratio
    div_stable = prior_div * multiple ** 3

    target_ok = div_target <= cap and (de - div_target) >= target_floor
    stable_ok = div_stable <= cap and (de - div_stable) >= stable_floor

    if target_ok and stable_ok:
        final = "target_payout" if div_target >= div_stable else "stable_growth"
    elif target_ok:
        final = "target_payout"
    elif stable_ok:
        final = "stable_growth"
    else:
        final = "no_feasible_policy"

    return {
        "final": final,
        "slots": {"one_period_growth_multiple_checkpoint": multiple},
    }
