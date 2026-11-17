"""h059 -- fictional transfer-monitoring policy with a staged corridor-threshold reduction.

Literal transcription of the question, sentence by sentence.
"""

import re
from fractions import Fraction

from finreason.nums import grab, grab_all, F

TEMPLATE_ID = "h059"


def _flag(name: str, text: str) -> bool:
    m = re.search(name + r"\s+flag of\s+(true|false)", text, flags=re.I)
    if m is None:
        raise ValueError(f"flag not found: {name}")
    return m.group(1).lower() == "true"


def solve(text: str, q: dict) -> dict:
    # "Current-window activity consists of A and B, while comparable historical-window activity was H."
    daytime_volume, overnight_volume = grab_all(r"Current-window activity consists of {N} and {N}", text)
    historical_volume = grab(r"historical-window activity was {N}", text)

    # "Define the current-volume growth ratio as (daytime + overnight - historical) / historical;
    #  its strict trigger threshold is G."
    growth_ratio = (daytime_volume + overnight_volume - historical_volume) / historical_volume
    growth_threshold = grab(r"strict trigger threshold is {N}", text)

    # "Transfers involving the scenario's elevated-risk corridor total C."
    corridor_transfers = grab(r"elevated-risk corridor total {N}", text)

    # "The baseline corridor threshold is T0."
    baseline_threshold = grab(r"baseline corridor threshold is {N}", text)

    # "At each of exactly three sequential adjustment stages, reduce the surviving threshold by
    #  fraction f of its then-current value ... effective threshold = baseline * (1 - f) three times."
    stages_word = re.search(r"At each of exactly (\w+) sequential adjustment stages", text)
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
    n_stages = 3
    if stages_word:
        w = stages_word.group(1).lower()
        n_stages = words.get(w, int(w) if w.isdigit() else 3)
    reduction_fraction = grab(r"reduce the surviving threshold by fraction {N}", text)
    retention_factor = 1 - reduction_fraction  # one-stage retention factor (checkpoint)
    effective_threshold = baseline_threshold
    for _ in range(n_stages):
        effective_threshold = effective_threshold * retention_factor

    # "The scenario also records a rapid-velocity flag of X, an incomplete-originator flag of Y,
    #  and a mandatory-hold flag of Z."
    rapid_velocity = _flag("rapid-velocity", text)
    incomplete_originator = _flag("incomplete-originator", text)
    mandatory_hold = _flag("mandatory-hold", text)

    # "The investigation trigger is true when both the growth threshold and effective corridor
    #  threshold are strictly exceeded, or when either metadata flag is present."
    growth_exceeded = growth_ratio > growth_threshold
    corridor_exceeded = corridor_transfers > effective_threshold
    investigation_trigger = (growth_exceeded and corridor_exceeded) or rapid_velocity or incomplete_originator

    # "Return Hold when the investigation trigger and mandatory-hold flag are both true; otherwise
    #  return Investigate when the investigation trigger is true; otherwise return Routine monitoring."
    if investigation_trigger and mandatory_hold:
        action = "Hold"
    elif investigation_trigger:
        action = "Investigate"
    else:
        action = "Routine monitoring"

    return {
        "final": action,
        "slots": {"corridor_threshold_residual_factor_checkpoint": Fraction(retention_factor)},
    }
