"""h104 -- two financing scenarios screened by a WACC cap and a staged D/(D+E) covenant ceiling.

AMBIGUITY HUNT (resolved from the text; every resolution is quoted):

 1. WACC formula / tax shield.  The text gives a "corporate tax rate ratio" and a "PRE-tax cost of
    debt percentage", so the after-tax cost of debt kd*(1-tau) is what enters the weighted average:
        WACC = E/(D+E) * ke + D/(D+E) * kd * (1 - tau)          (all in percent)
    Weights are the stated "equity value" / "debt value" (no other values exist).  The verdict in
    every instance is the same with or without the tax shield, so the branch outcome is robust.
 2. Units.  tau is a "ratio" (0.25 == 25%), ke / kd / the cap are "percentage" numbers, so the
    WACC is computed in percent and compared directly with "maximum permitted WACC percentage".
    The checkpoint spec unit is "ratio" and the ceiling "starts at 1.00", so ceilings stay ratios.
 3. Debt ratio base.  Explicit: "debt ratio means debt divided by debt plus equity, D/(D+E)"; the
    scenario's own D and E are used (no capping or substitution of the covenant value).
 4. Covenant mechanics.  "reduces the remaining ceiling by the same fraction t" is multiplicative
    (the text itself states "the final shared ceiling is (1-t)^3"), starting from the stated 1.00.
    Checkpoint one_stage_debt_ratio_cap_checkpoint = ceiling remaining after ONE stage
    = 1.00 * (1 - t)  (identical under the additive reading, so it is unambiguous).  Returned
    unrounded; in one instance it is 0.8000005, i.e. exactly on the 6-dp half-up tie, which the
    framework's half-up rendering handles (0.800001).  The QUALIFICATION test uses the FINAL
    ceiling (1-t)^n, n = number of stages (3, parsed from "(1-t)^3" when present).
 5. Strictness.  "maximum permitted WACC" and "permitted ceiling" are inclusive limits:
    qualify iff WACC <= max AND D/(D+E) <= final ceiling.  No instance sits exactly on a limit
    (checked exactly), so <= vs < cannot change any outcome; <= is the literal reading.
 6. Both limits are required ("qualifies only if both ... satisfy their limits") -- AND, not OR.
 7. Selection.  Among qualifiers pick the lower EXACT (unrounded, Fraction) WACC; on an exact tie
    return `Scenario A` (so A wins when WACC_A <= WACC_B); if neither qualifies -> `Neither scenario`;
    if exactly one qualifies it is returned regardless of its WACC relative to the other.
 8. No rounding anywhere inside the computation (nothing in the text says a rounded value is reused).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, grab_all, NUMBER, F

TEMPLATE_ID = "h104"

_WORD_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _scenario(label: str, text: str) -> dict:
    vals = grab_all(
        rf"Scenario {label} has equity value {{N}},?\s*debt value {{N}},?\s*"
        rf"cost of equity percentage {{N}},?\s*and pre-tax cost of debt percentage {{N}}",
        text,
    )
    e, d, ke, kd = vals
    return {"E": e, "D": d, "ke": ke, "kd": kd}


def _n_stages(text: str) -> int:
    # Prefer the explicit exponent in "(1-t)^3"; fall back to "exactly three ... stages"; else 3.
    m = re.search(r"\(\s*1\s*-\s*t\s*\)\s*\^\s*(\d+)", text)
    if m:
        return int(m.group(1))
    m = re.search(r"exactly\s+(\w+)\s+sequential covenant stages", text)
    if m:
        w = m.group(1).lower()
        if w in _WORD_NUM:
            return _WORD_NUM[w]
        if w.isdigit():
            return int(w)
    return 3


def _wacc(s: dict, tau: Fraction) -> Fraction:
    v = s["D"] + s["E"]
    return (s["E"] / v) * s["ke"] + (s["D"] / v) * s["kd"] * (1 - tau)


def _debt_ratio(s: dict) -> Fraction:
    return s["D"] / (s["D"] + s["E"])


def solve(text: str, q: dict) -> dict:
    tau = grab(r"corporate tax rate ratio {N}", text)                    # ratio, e.g. 0.25
    wacc_max = grab(r"maximum permitted WACC percentage {N}", text)       # percent
    t = grab(r"same fraction\s+t\s*=\s*{N}", text)                        # per-stage reduction fraction
    try:
        cap0 = grab(r"permitted ceiling starts at {N}", text)
    except ValueError:
        cap0 = Fraction(1)
    n = _n_stages(text)

    cap_after_one = cap0 * (1 - t)            # checkpoint: ceiling remaining after one stage
    cap_final = cap0 * (1 - t) ** n           # binding ceiling for qualification

    A = _scenario("A", text)
    B = _scenario("B", text)

    wacc_a, wacc_b = _wacc(A, tau), _wacc(B, tau)
    dr_a, dr_b = _debt_ratio(A), _debt_ratio(B)

    ok_a = (wacc_a <= wacc_max) and (dr_a <= cap_final)
    ok_b = (wacc_b <= wacc_max) and (dr_b <= cap_final)

    if ok_a and ok_b:
        final = "Scenario A" if wacc_a <= wacc_b else "Scenario B"   # exact tie -> A
    elif ok_a:
        final = "Scenario A"
    elif ok_b:
        final = "Scenario B"
    else:
        final = "Neither scenario"

    return {
        "final": final,
        "slots": {"one_stage_debt_ratio_cap_checkpoint": cap_after_one},
    }
