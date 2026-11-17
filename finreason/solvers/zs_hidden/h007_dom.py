# h007 -- two-bond comparison on holding-period return with a duration screen.
#
# FINANCE MODEL
# -------------
# For each bond i in {A, B}, all quantities are per-unit cash amounts over the common holding horizon:
#   R_i   = expected redemption cash                 (given)
#   C_i   = aggregate coupon cash over the horizon   (given)
#   P_i   = clean price                              (given)
#   S_i   = settlement cost                          (given)
#           Per the text it is ALL acquisition cash beyond the clean quote (accrued interest + fees),
#           so it is added exactly once and nothing else (no separate accrued interest) is added.
#   D_i   = modified duration                        (given; same convention/basis, used only as a screen)
#
#   total received cash     T_i = R_i + C_i
#   total acquisition outlay O_i = P_i + S_i                     <- checkpoint (usd, 2dp half-up)
#   holding-period return   h_i = (T_i - O_i) / O_i               (plain ratio, NOT annualised, NOT discounted)
#
# Qualification (exact comparisons on Fractions, no rounding anywhere):
#   bond i qualifies  <=>  h_i >= H_min   (at least, inclusive)   AND   D_i <= D_max   (at most, inclusive)
#   H_min is the "exact ratio" in the text (a plain ratio, e.g. 0.05 = 5%), D_max the duration cap.
#
# Decision:
#   - if both qualify: pick the one with the strictly higher exact h; on an exact tie pick Bond A
#   - if exactly one qualifies: pick it
#   - if neither: "Neither"
#
# Overrides of standard conventions: none. The duration is NOT used in any return calculation
# (it is only a screen); coupons are not reinvested; no time value adjustment is made.
# Checkpoints are the unrounded outlays; the framework rounds them half-up to 2 decimals.

import re
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h007"


def _bond_params(label: str, text: str) -> dict:
    """Parse the five inputs for 'Bond <label>' from the sentence 'Bond X has ...'."""
    # Isolate the sentence describing this bond so the other bond's numbers can never leak in.
    m = re.search(r"Bond " + label + r" has (.*?)modified duration\s+(-?\d[\d,]*(?:\.\d+)?(?:/\d+)?)", text, flags=re.S)
    if m is None:
        raise ValueError(f"bond {label} sentence not found")
    seg = "Bond " + label + " has " + m.group(1) + "modified duration " + m.group(2)
    return {
        "redemption": grab(r"redemption cash {N}", seg),
        "coupons": grab(r"coupon cash {N}", seg),
        "clean": grab(r"clean price {N}", seg),
        "settle": grab(r"settlement cost {N}", seg),
        "duration": grab(r"modified duration {N}", seg),
    }


def solve(text: str, q: dict) -> dict:
    a = _bond_params("A", text)
    b = _bond_params("B", text)

    min_ret = grab(r"at least the exact ratio {N}", text)
    max_dur = grab(r"modified duration is at most {N}", text)

    def metrics(p):
        received = p["redemption"] + p["coupons"]
        outlay = p["clean"] + p["settle"]
        ret = (received - outlay) / outlay
        ok = (ret >= min_ret) and (p["duration"] <= max_dur)
        return outlay, ret, ok

    out_a, ret_a, ok_a = metrics(a)
    out_b, ret_b, ok_b = metrics(b)

    if ok_a and ok_b:
        final = "Bond B" if ret_b > ret_a else "Bond A"  # exact tie -> Bond A
    elif ok_a:
        final = "Bond A"
    elif ok_b:
        final = "Bond B"
    else:
        final = "Neither"

    return {
        "final": final,
        "slots": {
            "a_outlay_checkpoint": out_a,
            "b_outlay_checkpoint": out_b,
        },
    }
