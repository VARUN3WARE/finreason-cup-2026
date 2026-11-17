"""h027 -- target-payout vs three-period stable-growth dividend policy (juror 4).

Rules encoded (one per sentence of the question):
  * distributable earnings DE = forecast net income - mandatory reserve
  * target-payout dividend  D_t = DE * payout ratio;  retained_t = DE - D_t, floor: retained_t >= floor_t (non-strict)
  * stable-growth dividend  D_s = prior dividend * (1 + g)^n  (n = 3 periods, g used exactly as stated, no rounding);
    retained_s = DE - D_s, floor: retained_s >= floor_s (non-strict)
  * a policy qualifies only if D <= cap (non-strict) AND its own retained floor is met
  * both qualify -> target_payout if D_t >= D_s (tie goes to target_payout) else stable_growth
  * one qualifies -> that one;  none -> no_feasible_policy
  * checkpoint: one-period growth multiple = 1 + g (unrounded; framework rounds to 6 dp half-up)
"""
from fractions import Fraction

from finreason.nums import grab, F

TEMPLATE_ID = "h027"

_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
          "nine": 9, "ten": 10}


def _periods(text: str) -> int:
    import re
    m = re.search(r"compounds it for exactly (\w+) periods?", text)
    if m:
        w = m.group(1).lower()
        if w in _WORDS:
            return _WORDS[w]
        if w.isdigit():
            return int(w)
    m = re.search(r"(\w+)-period stable-growth", text)
    if m and m.group(1).lower() in _WORDS:
        return _WORDS[m.group(1).lower()]
    return 3


def solve(text: str, q: dict) -> dict:
    ni = grab(r"forecast net income is {N}", text)
    reserve = grab(r"mandatory reserve is {N}", text)
    de = ni - reserve

    payout = grab(r"distributable earnings times {N}", text)
    floor_t = grab(r"target-payout policy proposes.*?requires retained distributable earnings of at least {N}", text)

    prior = grab(r"prior total cash dividend {N}", text)
    rate = grab(r"per-period rate {N}", text)
    floor_s = grab(r"stable-growth policy starts.*?requires retained distributable earnings of at least {N}", text)
    n = _periods(text)

    cap = grab(r"does not exceed {N}", text)

    mult = 1 + rate
    div_t = de * payout
    div_s = prior * mult ** n

    ret_t = de - div_t
    ret_s = de - div_s

    ok_t = div_t <= cap and ret_t >= floor_t
    ok_s = div_s <= cap and ret_s >= floor_s

    if ok_t and ok_s:
        final = "target_payout" if div_t >= div_s else "stable_growth"
    elif ok_t:
        final = "target_payout"
    elif ok_s:
        final = "stable_growth"
    else:
        final = "no_feasible_policy"

    return {"final": final, "slots": {"one_period_growth_multiple_checkpoint": Fraction(mult)}}
