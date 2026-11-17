"""h015 -- three-stage payout ratchet vs. liquidity cap (skeptical / ambiguity-hunting analyst).

STRUCTURE
  net income NI, mandatory retention R (both USD millions)
  distributable earnings      DE  = NI - R
  stage share after k stages  s_k = s_0 * (1 - t)^k   with s_0 = 100% = 1 (ratio)
  policy limit                PL  = DE * (1 - t)^3
  liquidity cap               C
  final                       min(PL, C)            (USD millions, unrounded; framework rounds half-up 2dp)
  checkpoint one_stage_payout_factor_checkpoint = s_1 = 1 - t   (ratio, framework rounds half-up 6dp)

AMBIGUITIES CONSIDERED AND RESOLUTIONS (with textual evidence)
 A1. Base of the ratchet: "dividend authorization starts at 100% of distributable earnings" and
     "must FIRST retain R" -> retention is deducted before anything else; DE = NI - R, and the
     ratchet applies to DE, not to NI.  Retention is a monetary amount ("all monetary amounts in
     USD millions"), not a percentage (no % sign, no word "percent").
 A2. Multiplicative vs. additive ratchet: "reduces the remaining authorized share by the same
     fraction t" could in isolation mean t percentage points, but the sentence itself fixes it:
     "so the policy limit is distributable earnings times (1-t)^3" -> multiplicative.  Either
     reading gives the same one-stage checkpoint (1 - t) anyway since the start is exactly 1.
 A3. Unit of t: written "t=0.2" with no % sign -> already a ratio; do NOT divide by 100.
 A4. Checkpoint quantity/unit: "authorized payout share remaining after one ratchet stage",
     spec unit "ratio" -> the SHARE (a dimensionless fraction) remaining, i.e. s_1 = 1*(1-t) = 1-t,
     NOT the monetary amount DE*(1-t), NOT the reduction t itself ("remaining"), and as a plain
     ratio (0.8), not percent (80).
 A5. Number of stages: "exactly three sequential payout-ratchet stages" and "(1-t)^3" -> 3.
     Parsed from the "(1-t)^k" exponent (fallback: the word before "sequential").
 A6. Combination of the two limits: "liquidity plan SEPARATELY caps the cash dividend" and
     "maximum total cash dividend satisfying BOTH limits" -> min(PL, C).  The cap is not an input
     to the ratchet; the branch (policy-bound vs. cap-bound) may differ across instances.
 A7. Rounding: "use exact arithmetic through all intermediate steps, round only the final value"
     -> everything exact Fractions; return unrounded; framework rounds (2dp final, 6dp checkpoint).
     Nothing in the text says any rounded value is fed downstream.
 A8. Floor at zero: the text states no floor; if NI < R the policy limit would be negative and
     min() would return it.  Implemented exactly as worded (no floor); all 3 instances have NI > R.
 A9. "100%" starting share is parsed (as percent / 100) rather than assumed, so a variant that
     starts at e.g. 90% would still be honoured.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import F, grab

TEMPLATE_ID = "h015"

_WORD_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _stages(text: str) -> int:
    # Primary: the explicit exponent in "(1-t)^3" (tolerate spaces / unicode minus).
    m = re.search(r"\(\s*1\s*[-−]\s*t\s*\)\s*\^\s*\{?\s*(\d+)", text)
    if m:
        return int(m.group(1))
    # Fallback: "exactly three sequential ..." (word or digit).
    m = re.search(r"exactly\s+(\w+)\s+sequential", text, flags=re.I)
    if m:
        w = m.group(1).lower()
        if w.isdigit():
            return int(w)
        if w in _WORD_NUM:
            return _WORD_NUM[w]
    raise ValueError("could not determine number of ratchet stages")


def _start_share(text: str) -> Fraction:
    # "dividend authorization starts at 100% of distributable earnings"
    m = re.search(r"starts\s+at\s+(-?\d+(?:\.\d+)?(?:/\d+)?)\s*(%|percent)", text, flags=re.I)
    if m:
        return F(m.group(1)) / 100
    return Fraction(1)


def solve(text: str, q: dict) -> dict:
    ni = grab(r"net income of {N}", text)                       # USD millions
    retain = grab(r"must first retain {N}", text)               # USD millions
    t = grab(r"\bt\s*=\s*{N}", text)                            # ratio (already a fraction)
    cap = grab(r"caps the cash dividend at {N}", text)          # USD millions
    n_stages = _stages(text)
    s0 = _start_share(text)

    distributable = ni - retain                                 # A1
    one_stage_share = s0 * (1 - t)                              # A2/A4: ratio after one stage
    policy_limit = distributable * s0 * (1 - t) ** n_stages     # A5
    final = min(policy_limit, cap)                              # A6 (no floor, A8)

    return {
        "final": final,
        "slots": {"one_stage_payout_factor_checkpoint": one_stage_share},
    }
