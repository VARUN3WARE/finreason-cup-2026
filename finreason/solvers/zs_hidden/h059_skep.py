"""h059 -- scenario-local transaction-monitoring policy (skeptical / ambiguity-hunting analyst).

Structure (shared by all 3 instances):
  daytime A, overnight B, historical H
  growth ratio       = (A + B - H) / H                         (plain ratio)
  growth trigger     : growth ratio  >  G        (STRICT; text: "its strict trigger threshold is G")
  corridor transfers C, baseline threshold T0, per-stage reduction fraction f, S (= "three") stages
  effective thresh   = T0 * (1 - f) ** S                      (text: "baseline multiplied by one minus
                                                               that fraction three successive times")
  corridor trigger   : C  >  effective threshold (STRICT; text: "strictly exceeded")
  investigation trigger = (growth trigger AND corridor trigger) OR rapid_velocity OR incomplete_originator
  action: Hold if trigger and mandatory_hold; else Investigate if trigger; else Routine monitoring

AMBIGUITIES CONSIDERED AND RESOLVED
-----------------------------------
A1. Which flags are the "metadata flags" in "or when either metadata flag is present"?
    Three flags are listed: rapid-velocity, incomplete-originator, mandatory-hold.  "Either" denotes one
    of TWO, and the two flags describing transaction metadata are rapid-velocity and incomplete-originator.
    Mandatory-hold is a policy directive consumed only by the final decision ("Return Hold when the
    investigation trigger and mandatory-hold flag are both true").  If mandatory-hold also fed the trigger,
    that conjunction would degenerate to "mandatory-hold is true", which the text's structure rules out.
    => metadata flags = {rapid-velocity, incomplete-originator}; mandatory-hold is NOT a trigger.
    (Consequence: an instance with growth exceeded, corridor not exceeded, both metadata flags false and
    mandatory-hold true resolves to "Routine monitoring", not "Hold".)
A2. Growth comparison: the growth ratio is a plain ratio ((A+B-H)/H) and the threshold is quoted as a
    plain number ("0.6", "0", "2"), so compare ratio-to-ratio with no percent conversion.  "strict
    trigger threshold" + "strictly exceeded" => strict ">".
A3. Corridor comparison: transfers C vs effective threshold, strict ">" ("strictly exceeded").  No
    rounding of the effective threshold before comparison (none is stated).
A4. Effective threshold: multiplicative compounding T0*(1-f)^S, NOT T0*(1-S*f); the text says the
    fraction applies to the "then-current value" and "one minus that fraction three successive times".
    S is parsed from the word ("three") with a fallback of 3.
A5. Checkpoint "corridor-threshold fraction retained after one stage" / "one-stage corridor-threshold
    retention factor" = 1 - f (a ratio), NOT the threshold value T0*(1-f) and NOT the three-stage
    factor (1-f)^3.  Unit "ratio" confirms a dimensionless fraction.  Returned unrounded; the framework
    applies half-up to 6 dp.  The rounded checkpoint is never fed back into the computation.
A6. Order of A and B ("consists of 11 and 9"): only their sum matters, so the assignment to
    daytime/overnight is irrelevant.
A7. Flag wording: "flag of true/false"; parsing also tolerates yes/no, present/absent, set/clear,
    on/off, 1/0 in case a sibling instance phrases it differently.
A8. Reduction fraction quoted as a fraction ("by fraction 0.1876547"); if an instance instead said
    "by N percent" the value is divided by 100.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h059"

_WORD_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}

_TRUE = {"true", "yes", "present", "set", "on", "1", "raised", "active"}
_FALSE = {"false", "no", "absent", "clear", "cleared", "off", "0", "not present", "inactive"}


def _flag(text: str, name: str) -> bool:
    """Parse '<name> flag of <value>' (also '<name> flag is <value>')."""
    m = re.search(
        rf"{name}\s+flag\s+(?:of|is|=|:)?\s*(true|false|yes|no|present|absent|not present|set|clear|cleared|on|off|1|0|raised|active|inactive)\b",
        text,
        flags=re.I,
    )
    if m is None:
        raise ValueError(f"flag not found: {name!r}")
    v = m.group(1).lower()
    if v in _TRUE:
        return True
    if v in _FALSE:
        return False
    raise ValueError(f"unrecognised flag value {v!r} for {name!r}")


def _stages(text: str) -> int:
    m = re.search(r"exactly\s+(\w+)\s+sequential\s+adjustment\s+stages", text, flags=re.I)
    if m is None:
        m = re.search(rf"(?:fraction\s+)?(\w+)\s+successive\s+times", text, flags=re.I)
    if m is None:
        return 3
    w = m.group(1).lower()
    if w in _WORD_NUM:
        return _WORD_NUM[w]
    if w.isdigit():
        return int(w)
    return 3


def _reduction_fraction(text: str) -> Fraction:
    # "reduce the surviving threshold by fraction 0.1876547 of its then-current value"
    m = re.search(rf"reduce the surviving threshold by\s+(?:a\s+)?fraction\s+({NUMBER})", text, flags=re.I)
    if m is not None:
        return F(m.group(1))
    m = re.search(rf"reduce the surviving threshold by\s+({NUMBER})\s*(percent|%)", text, flags=re.I)
    if m is not None:
        return F(m.group(1)) / 100
    m = re.search(rf"reduce the surviving threshold by\s+({NUMBER})", text, flags=re.I)
    if m is not None:
        return F(m.group(1))
    raise ValueError("reduction fraction not found")


def solve(text: str, q: dict) -> dict:
    # --- volumes -------------------------------------------------------------------------------
    m = re.search(rf"Current-window activity consists of\s+({NUMBER})\s+and\s+({NUMBER})", text, flags=re.I)
    if m is None:
        raise ValueError("current-window volumes not found")
    day = F(m.group(1))
    night = F(m.group(2))
    hist = grab(r"historical-window activity was\s+{N}", text)

    # --- growth trigger (strict) -----------------------------------------------------------
    growth_threshold = grab(r"strict trigger threshold is\s+{N}", text)
    growth_ratio = (day + night - hist) / hist
    growth_exceeded = growth_ratio > growth_threshold

    # --- corridor trigger (strict) ---------------------------------------------------------
    transfers = grab(r"elevated-risk corridor total\s+{N}", text)
    baseline = grab(r"baseline corridor threshold is\s+{N}", text)
    f = _reduction_fraction(text)
    stages = _stages(text)
    retained_one_stage = Fraction(1) - f                    # checkpoint (ratio), unrounded
    effective_threshold = baseline * retained_one_stage ** stages
    corridor_exceeded = transfers > effective_threshold

    # --- flags ---------------------------------------------------------------------------------
    rapid_velocity = _flag(text, "rapid-velocity")
    incomplete_originator = _flag(text, "incomplete-originator")
    mandatory_hold = _flag(text, "mandatory-hold")

    # --- investigation trigger (A1: metadata flags are rapid-velocity & incomplete-originator only)
    trigger = (growth_exceeded and corridor_exceeded) or rapid_velocity or incomplete_originator

    if trigger and mandatory_hold:
        action = "Hold"
    elif trigger:
        action = "Investigate"
    else:
        action = "Routine monitoring"

    return {
        "final": action,
        "slots": {
            "corridor_threshold_residual_factor_checkpoint": retained_one_stage,
        },
    }
