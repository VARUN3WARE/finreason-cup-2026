"""h027 -- target-payout vs three-period stable-growth dividend policy (enum answer).

AMBIGUITY HUNT (each resolved from the question text):

 1. Distributable earnings (DE).  Text: "distributable earnings equal forecast net income
    minus the reserve"  ->  DE = NI - reserve.  USD millions throughout; no unit conversion.

 2. Target-payout dividend.  Text: "terminal total dividend equal to distributable earnings
    times 0.4".  The 0.4 is a plain multiplier (word "times", no "percent"), so no /100.
    D_t = DE * payout_ratio.

 3. Stable-growth dividend.  Text: "compounds it for exactly three periods at the per-period
    rate 0.2345675 ... equals the prior total cash dividend times (1 + the growth rate)^3".
    The rate is a plain per-period ratio (no "percent"), so no /100.  Exponent is the integer
    3 (Fraction ** int, exact).  D_s = D0 * (1 + g) ** 3.  Dividends are NOT rounded anywhere
    (nothing in the text says "to the nearest ...", "whole", "cents", etc.).

 4. Checkpoint "one-period growth multiple used by the stable policy".  "One-period" rules out
    (1+g)^3 (the three-period multiple) and "multiple" rules out the bare rate g; the multiple
    applied once per period is 1 + g.  Unit "multiple" = plain ratio, reported unrounded
    (framework rounds half-up to 6 dp).

 5. "Retained distributable earnings" for a policy = DE minus THAT policy's proposed dividend
    ("policy-specific retained-earnings floor").  Floor test: "at least X"  ->  retained >= X
    (non-strict).  Each policy has its own floor (104 vs 94 in instance 1); the first floor
    number belongs to the target-payout sentence, the second to the stable-growth sentence.

 6. Dividend cap.  "qualifies only if its proposed dividend does not exceed 88"  ->  D <= cap
    (non-strict: an exact tie with the cap still qualifies).  Same cap applies to both policies.

 7. Qualification = (D <= cap) AND (DE - D >= policy floor).  Both conditions required ("only if
    ... and ...").

 8. Decision.  Both qualify: "return target_payout when the target-payout dividend is at least
    the stable-growth dividend, including an exact tie; otherwise stable_growth"
    ->  D_t >= D_s  => target_payout, else stable_growth.  Exactly one qualifies: return that
    one.  Neither: no_feasible_policy.  Comparison is on the proposed dividend amounts
    (not on retained earnings), done with exact Fractions so ties are detected exactly.

 9. Number parsing is anchored on the surrounding words so instance values are never hardcoded.
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h027"


def solve(text: str, q: dict) -> dict:
    # --- inputs -------------------------------------------------------------------------
    net_income = grab(r"forecast net income is {N}", text)
    reserve = grab(r"mandatory reserve is {N}", text)
    payout_ratio = grab(r"equal to distributable earnings times {N}", text)
    target_floor = grab(
        r"times {N} and requires retained distributable earnings of at least {N}", text, group=2
    )
    prior_dividend = grab(r"prior total cash dividend {N} at the beginning", text)
    growth_rate = grab(r"at the per-period rate {N}", text)
    stable_floor = grab(
        r"\^3; it requires retained distributable earnings of at least {N}", text
    )
    dividend_cap = grab(r"proposed dividend does not exceed {N}", text)

    # --- computation ----------------------------------------------------------------------
    distributable = net_income - reserve                      # DE = NI - reserve

    growth_multiple = Fraction(1) + growth_rate               # one-period multiple (checkpoint)

    target_dividend = distributable * payout_ratio            # D_t = DE * ratio
    stable_dividend = prior_dividend * growth_multiple ** 3   # D_s = D0 * (1+g)^3, exact

    target_retained = distributable - target_dividend
    stable_retained = distributable - stable_dividend

    target_ok = (target_dividend <= dividend_cap) and (target_retained >= target_floor)
    stable_ok = (stable_dividend <= dividend_cap) and (stable_retained >= stable_floor)

    if target_ok and stable_ok:
        final = "target_payout" if target_dividend >= stable_dividend else "stable_growth"
    elif target_ok:
        final = "target_payout"
    elif stable_ok:
        final = "stable_growth"
    else:
        final = "no_feasible_policy"

    return {
        "final": final,
        "slots": {"one_period_growth_multiple_checkpoint": growth_multiple},
    }
