"""Hidden cluster h049 -- multi-layer assurance envelope check (skeptic / ambiguity-hunting analyst).

Structure of the question
-------------------------
  reported energy savings E_r  vs audited energy savings E_a
  reported waste-management savings W_r vs audited waste-management savings W_a
  per-layer tolerance ratio t applied at exactly k (= three) sequential multiplicative layers:
      lower envelope = reported * (1 - t)^k ,  upper envelope = reported * (1 + t)^k   (inclusive)
  audit coverage c "must reach" threshold c_min
  a boolean flag ("true"/"false") saying the engagement covered both metrics and issued an unmodified conclusion
  final: "assured" only when EVERY condition holds, else "review_required"
  checkpoint lower_stage_factor_checkpoint: "the one-layer lower tolerance factor"

Ambiguities hunted and resolved (with textual evidence)
-------------------------------------------------------
A1  Checkpoint = 1 - t (single layer) vs (1 - t)^3 (full envelope factor).
    Evidence: description says "one-layer lower tolerance factor"; slot id is lower_STAGE_factor (one stage = one layer);
    the text itself defines the per-layer step as "multiplies the current lower bound by 1-t".  -> 1 - t, unrounded.
    (Note t = 0.0999995 gives exactly 0.9000005, which half-up rounds to 0.900001 -- Fraction arithmetic keeps that exact.)
A2  t is a ratio, not a percent: "per-layer tolerance ratio 0.2".  -> used as-is.  Defensive: if the text ever says
    "tolerance ... percent" the value is divided by 100.
A3  Which quantity is enveloped and which is compared: "Starting from each reported amount ... the audited amount is
    compared once against the final inclusive envelope reported*(1-t)^3 through reported*(1+t)^3".
    -> envelope built on REPORTED, AUDITED is tested.  Never the reverse.
A4  Inclusive vs strict envelope: "final inclusive envelope"  -> lower <= audited <= upper (both ends inclusive).
A5  Number of layers: "exactly three sequential multiplicative audit-adjustment layers" and the explicit "^3".
    -> k = 3; parsed from the "^N" exponent if present, else from the number word, default 3 (never hardcoded blindly).
A6  Compounding: "every layer multiplies the current lower bound by 1-t and the current upper bound by 1+t"
    -> multiplicative compounding (1-t)^k, NOT additive 1-3t.  The formula in the text confirms this.
A7  Coverage comparison: "Audit coverage 0.9 must reach 0.8"  -> "reach" = at least  -> c >= c_min (non-strict).
A8  Boolean flag: "true indicates that the completed engagement covered both metrics and issued an unmodified
    conclusion".  The token is an instance-level input that could be "false" in another instance -> parsed, and the
    condition holds only if it is literally true.
A9  Both metrics must pass: "Return assured only when every condition holds" -> energy envelope AND waste envelope AND
    coverage AND flag.  Any failure -> review_required.
A10 No intermediate rounding anywhere (nothing in the text says a rounded value is reused).  All exact Fractions.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h049"

_WORD_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _pair(text: str, metric: str) -> tuple[Fraction, Fraction]:
    """(reported, audited) for a metric name such as 'energy' or 'waste-management'."""
    m = re.escape(metric)
    pat = rf"reported {m} savings\s+{{N}}\s+against audited {m} savings\s+{{N}}"
    rx = pat.replace("{N}", f"({NUMBER})")
    mo = re.search(rx, text, flags=re.S | re.I)
    if mo is None:
        raise ValueError(f"could not find reported/audited pair for {metric!r}")
    return F(mo.group(1)), F(mo.group(2))


def _tolerance(text: str) -> Fraction:
    mo = re.search(rf"tolerance (ratio|rate|percentage|percent)?\s*(?:of\s+)?({NUMBER})\s*(percent|%)?", text, flags=re.I)
    if mo is None:
        raise ValueError("tolerance not found")
    t = F(mo.group(2))
    unit_word = (mo.group(1) or "").lower()
    trailing = (mo.group(3) or "").lower()
    if trailing in ("percent", "%") or unit_word in ("percentage", "percent"):
        t = t / 100  # A2 defensive: only triggers if the text explicitly says percent
    return t


def _layers(text: str) -> int:
    # Prefer the explicit exponent in the envelope formula "reported*(1-t)^3".
    mo = re.search(r"\(1-t\)\^(\d+)", text)
    if mo:
        return int(mo.group(1))
    mo = re.search(r"exactly\s+(\w+)\s+sequential", text, flags=re.I)
    if mo:
        w = mo.group(1).lower()
        if w.isdigit():
            return int(w)
        if w in _WORD_NUM:
            return _WORD_NUM[w]
    return 3


def _flag(text: str) -> bool:
    mo = re.search(r"\b(true|false)\s+indicates\s+that", text, flags=re.I)
    if mo is None:
        raise ValueError("boolean flag not found")
    return mo.group(1).lower() == "true"


def solve(text: str, q: dict) -> dict:
    e_rep, e_aud = _pair(text, "energy")
    w_rep, w_aud = _pair(text, "waste-management")
    t = _tolerance(text)
    k = _layers(text)

    cov = grab(r"[Aa]udit coverage\s+{N}", text)
    cov_min = grab(r"must reach\s+{N}", text)
    flag = _flag(text)

    lower_factor = 1 - t            # A1: one-layer lower tolerance factor (checkpoint)
    upper_factor = 1 + t
    low_k = lower_factor ** k       # A5/A6: multiplicative compounding over k layers
    up_k = upper_factor ** k

    def within(rep: Fraction, aud: Fraction) -> bool:
        # A3: envelope on reported; audited compared.  A4: inclusive on both ends.
        return rep * low_k <= aud <= rep * up_k

    energy_ok = within(e_rep, e_aud)
    waste_ok = within(w_rep, w_aud)
    coverage_ok = cov >= cov_min    # A7: "must reach" -> at least

    final = "assured" if (energy_ok and waste_ok and coverage_ok and flag) else "review_required"  # A8/A9

    return {
        "final": final,
        "slots": {
            "lower_stage_factor_checkpoint": lower_factor,
        },
    }
