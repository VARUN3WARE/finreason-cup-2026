"""Hidden cluster h105: social-impact program scale meeting a surplus-ratio requirement.

Structure (from the text):
  combined fixed costs  C = launch cost + monitoring cost
  required social value R = C * (1 + surplus ratio)          ("equivalently ... one plus that ratio")
  scale                 n = R / value per unit                ("exactly meets" -> equality, no ceiling)

Checkpoint ``monitoring_surplus_value_checkpoint`` ("surplus requirement attributable to
monitoring cost", USD): the required surplus is the excess of required social value over the
combined fixed costs, C * ratio = launch*ratio + monitoring*ratio; the part attributable to the
monitoring cost is monitoring cost * surplus ratio.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h105"


def _ratio(label: str, text: str) -> Fraction:
    """Number after ``label``; converted from percent if the text states it in percent."""
    m = re.search(label + r"\s*(?:of\s*)?(" + NUMBER + r")\s*(percent|%)?", text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {label!r}")
    value = F(m.group(1))
    return value / 100 if m.group(2) else value


def solve(text: str, q: dict) -> dict:
    launch = grab(r"launch cost\s*(?:of\s*)?(?:USD\s*)?{N}", text)
    monitoring = grab(r"monitoring cost\s*(?:of\s*)?(?:USD\s*)?{N}", text)
    value_per_unit = grab(r"net monetized social value\s*(?:of\s*)?(?:USD\s*)?{N}", text)
    surplus = _ratio(r"surplus ratio", text)

    combined_fixed = launch + monitoring
    required_value = combined_fixed * (1 + surplus)
    if value_per_unit == 0:
        raise ValueError("value per unit is zero")
    scale = required_value / value_per_unit

    monitoring_surplus = monitoring * surplus

    values = {"monitoring_surplus_value_checkpoint": monitoring_surplus}
    slots = {}
    for s in q["trace_spec"]["slots"]:
        sid = s["slot_id"]
        if sid not in values:
            raise KeyError(f"unexpected slot {sid}")
        slots[sid] = values[sid]
    return {"final": scale, "slots": slots}
