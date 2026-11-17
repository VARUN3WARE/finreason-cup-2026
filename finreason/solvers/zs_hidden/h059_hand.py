"""h059: monitoring-policy decision with a multi-stage corridor-threshold reduction.

Growth ratio = (daytime + overnight - historical) / historical, strict trigger (>).
Effective corridor threshold = baseline * (1 - f) ** stages; corridor transfers must strictly exceed it.
Investigation trigger = (growth > thr AND corridor > effective) OR rapid-velocity OR incomplete-originator.
Action: Hold if trigger and mandatory-hold; else Investigate if trigger; else Routine monitoring.
Checkpoint: one-stage retention factor (1 - f), unrounded.
"""

import re
from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h059"

_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def _flag(name: str, text: str) -> bool:
    m = re.search(name + r"\s+flag\s+of\s+(true|false)", text, flags=re.I)
    if m is None:
        raise ValueError(f"flag not found: {name}")
    return m.group(1).lower() == "true"


def _stages(text: str) -> int:
    m = re.search(r"each of (?:exactly )?(\w+) sequential adjustment stages", text, flags=re.I)
    if m is None:
        raise ValueError("stage count not found")
    tok = m.group(1).lower()
    if tok.isdigit():
        return int(tok)
    return _WORDS[tok]


def solve(text: str, q: dict) -> dict:
    day, night = grab_all(r"Current-window activity consists of {N} and {N}", text)
    hist = grab(r"historical-window activity was {N}", text)
    growth_thr = grab(r"strict trigger threshold is {N}", text)
    corridor = grab(r"elevated-risk corridor total {N}", text)
    baseline = grab(r"baseline corridor threshold is {N}", text)
    frac = grab(r"reduce the surviving threshold by fraction {N}", text)
    stages = _stages(text)

    rapid = _flag("rapid-velocity", text)
    incomplete = _flag("incomplete-originator", text)
    mandatory_hold = _flag("mandatory-hold", text)

    growth = (day + night - hist) / hist
    retention = 1 - frac
    effective = baseline * retention ** stages

    trigger = (growth > growth_thr and corridor > effective) or rapid or incomplete

    if trigger and mandatory_hold:
        action = "Hold"
    elif trigger:
        action = "Investigate"
    else:
        action = "Routine monitoring"

    return {
        "final": action,
        "slots": {"corridor_threshold_residual_factor_checkpoint": retention},
    }
