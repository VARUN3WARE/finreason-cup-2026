"""h103 -- fictional transaction-review policy with a staged spike-threshold decay.

Structure (per instance):
  * related cash transactions -> aggregate volume = their sum;
  * aggregate review threshold;
  * historical average cash transaction, baseline spike-ratio threshold;
  * N sequential stages, each cutting the surviving spike threshold by fraction f of its
    then-current value (no replenishment) -> effective = baseline * (1 - f) ** N;
  * spike ratio = largest transaction / historical average;
  * two critical flags ("The policy also records <bool> and <bool>.").
Route: "Enhanced review" if (aggregate > threshold AND spike > effective) OR either flag is
true; otherwise "Standard review".
Checkpoint: one-stage threshold-retention factor = 1 - f (ratio, unrounded here).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h103"

_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def _count(token: str) -> int:
    token = token.strip().lower()
    if token.isdigit():
        return int(token)
    return _WORDS[token]


def _transactions(text: str) -> list[Fraction]:
    # "... cash transactions are 7, 2, and 1."  (list of numbers joined by commas / "and")
    lst = rf"(?:{NUMBER})(?:\s*,\s*(?:and\s+)?(?:{NUMBER})|\s+and\s+(?:{NUMBER}))*"
    m = re.search(rf"cash transactions are\s+({lst})", text)
    if m is None:
        raise ValueError("transaction list not found")
    vals = [F(v) for v in re.findall(NUMBER, m.group(1))]
    if not vals:
        raise ValueError("empty transaction list")
    return vals


def _stages(text: str) -> int:
    m = re.search(r"At each of (?:exactly )?(\w+) sequential adjustment stages", text)
    if m is None:
        m = re.search(r"one minus that fraction (\w+) successive times", text)
    if m is None:
        raise ValueError("stage count not found")
    return _count(m.group(1))


def _fraction(text: str) -> Fraction:
    m = re.search(rf"reduce the surviving spike threshold by fraction ({NUMBER})", text)
    if m is not None:
        return F(m.group(1))
    m = re.search(rf"reduce the surviving spike threshold by ({NUMBER})\s*(?:percent|%)", text)
    if m is not None:
        return F(m.group(1)) / 100
    raise ValueError("stage reduction fraction not found")


def _flags(text: str) -> list[bool]:
    m = re.search(r"The policy also records (true|false) and (true|false)", text, flags=re.I)
    if m is None:
        raise ValueError("critical flags not found")
    return [g.lower() == "true" for g in m.groups()]


def solve(text: str, q: dict) -> dict:
    tx = _transactions(text)
    aggregate = sum(tx, Fraction(0))
    agg_threshold = grab(r"aggregate review threshold is {N}", text)
    hist_avg = grab(r"historical average cash transaction is {N}", text)
    baseline = grab(r"baseline largest-to-history spike-ratio threshold is {N}", text)
    n_stages = _stages(text)
    f = _fraction(text)

    retention = 1 - f                         # threshold fraction retained after one stage
    effective = baseline * retention ** n_stages
    spike = max(tx) / hist_avg

    flag_a, flag_b = _flags(text)

    enhanced = (aggregate > agg_threshold and spike > effective) or flag_a or flag_b
    final = "Enhanced review" if enhanced else "Standard review"

    slot_ids = [s["slot_id"] for s in q["trace_spec"]["slots"]]
    slots = {}
    for sid in slot_ids:
        if "residual_factor" in sid or "retention" in sid or "retained" in sid:
            slots[sid] = retention
        else:
            raise ValueError(f"unknown slot {sid}")
    return {"final": final, "slots": slots}
