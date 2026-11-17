# FINANCE MODEL (assurance-engagement tolerance envelope)
# ---------------------------------------------------------------------------
# For every reported metric R_i (energy savings, waste-management savings) with audited
# amount A_i, a per-layer tolerance ratio t applies at exactly L sequential multiplicative
# layers (L = "three" in the text).  Each layer multiplies the current lower bound by (1-t)
# and the current upper bound by (1+t), so the final inclusive envelope is
#       [ R_i*(1-t)^L ,  R_i*(1+t)^L ]
# and the audited amount A_i is compared ONCE against it (no per-layer comparison).
# Inclusive: A_i == bound passes.  Exact Fraction arithmetic (t has up to 7 decimals), so
# boundary cases are exact.
#
# Further conditions (all must hold for "assured"):
#   * audit coverage (observed) must reach the minimum: "must reach" => observed >= required.
#   * the boolean flag stated in the text ("true indicates that the completed engagement
#     covered both metrics and issued an unmodified conclusion") must be true.
#   * every metric's audited amount lies inside its envelope.
# Otherwise "review_required".
#
# Checkpoint: lower_stage_factor_checkpoint = the ONE-layer lower tolerance factor = (1 - t),
# a plain ratio, reported UNROUNDED here (framework applies half-up to 6 dp; e.g.
# t = 0.0999995 -> 0.9000005 -> 0.900001 half-up).  Not the cubed factor.
# ---------------------------------------------------------------------------
import re
from fractions import Fraction

from finreason.nums import grab, grab_all, F, NUMBER

TEMPLATE_ID = "h049"

_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
          "eight": 8, "nine": 9, "ten": 10}


def _layers(text):
    m = re.search(r"exactly\s+(\w+)\s+sequential", text)
    if m:
        w = m.group(1).lower()
        if w in _WORDS:
            return _WORDS[w]
        if w.isdigit():
            return int(w)
    m = re.search(r"\(1[-+]t\)\^(\d+)", text)
    if m:
        return int(m.group(1))
    raise ValueError("layers not found")


def solve(text: str, q: dict) -> dict:
    t = grab(r"tolerance ratio {N}", text)
    layers = _layers(text)

    pairs = re.findall(
        r"reported ([A-Za-z][\w\- ]*?) (" + NUMBER + r") against audited \1 (" + NUMBER + r")", text)
    if not pairs:
        raise ValueError("no metric pairs")

    lo_f = (1 - t) ** layers
    hi_f = (1 + t) ** layers
    all_in = True
    for _name, rep, aud in pairs:
        rep, aud = F(rep), F(aud)
        if not (rep * lo_f <= aud <= rep * hi_f):
            all_in = False

    cov, req = grab_all(r"[Aa]udit coverage {N} must reach {N}", text)
    cov_ok = cov >= req

    mflag = re.search(r"\b(true|false)\s+indicates", text)
    flag_ok = (mflag.group(1) == "true") if mflag else True

    final = "assured" if (all_in and cov_ok and flag_ok) else "review_required"
    return {"final": final, "slots": {"lower_stage_factor_checkpoint": 1 - t}}
