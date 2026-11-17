# FINANCE MODEL (h059): fictional AML-style transaction-monitoring escalation policy.
#
#   growth      = (daytime + overnight - historical) / historical      (current-volume growth ratio)
#   growth_hit  = growth > growth_threshold                            (STRICT)
#   f           = per-stage reduction fraction (applied to the surviving threshold)
#   retention   = 1 - f                                                (one-stage retention factor; checkpoint)
#   effective   = baseline * (1 - f) ** 3                              (three sequential stages, no replenishment)
#   corridor_hit= corridor_transfers > effective                       (STRICT)
#   trigger     = (growth_hit AND corridor_hit) OR rapid_flag OR incomplete_originator_flag
#                 -- "either metadata flag" = the rapid-velocity and incomplete-originator flags.
#                 -- the mandatory-hold flag is NOT an input of the trigger; it only upgrades the action.
#   action      = "Hold"               if trigger AND mandatory_hold
#                 "Investigate"        elif trigger
#                 "Routine monitoring" otherwise
#
# Checkpoint: corridor_threshold_residual_factor_checkpoint = 1 - f, a plain ratio, returned UNROUNDED
# (framework applies half-up to 6 dp).
#
# Ambiguity resolved: mandatory-hold flag is excluded from "either metadata flag" (the sentence names
# two flags via "either"; the third flag is consumed by the action rule).

import re
from fractions import Fraction

from finreason.nums import grab, grab_all, F  # noqa: F401

TEMPLATE_ID = "h059"


def _flag(name: str, text: str) -> bool:
    m = re.search(name + r"\s+flag\s+of\s+(true|false)", text)
    if m is None:
        raise ValueError(f"flag not found: {name}")
    return m.group(1) == "true"


def solve(text: str, q: dict) -> dict:
    day, night = grab_all(r"activity consists of {N} and {N}", text)
    hist = grab(r"historical-window activity was {N}", text)
    g_thr = grab(r"strict trigger threshold is {N}", text)
    corridor = grab(r"elevated-risk corridor total {N}", text)
    baseline = grab(r"baseline corridor threshold is {N}", text)
    f = grab(r"reduce the surviving threshold by fraction {N}", text)

    rapid = _flag("rapid-velocity", text)
    incomplete = _flag("incomplete-originator", text)
    mandatory = _flag("mandatory-hold", text)

    growth = (day + night - hist) / hist
    retention = 1 - f
    effective = baseline * retention ** 3

    trigger = (growth > g_thr and corridor > effective) or rapid or incomplete

    if trigger and mandatory:
        action = "Hold"
    elif trigger:
        action = "Investigate"
    else:
        action = "Routine monitoring"

    return {
        "final": action,
        "slots": {"corridor_threshold_residual_factor_checkpoint": retention},
    }
