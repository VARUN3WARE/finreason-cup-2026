"""h005: carbon-credit break-even price vs internal abatement.

planned abatement = internal capacity * committed utilization
internal cost     = fixed mobilization cost + variable cost per ton * planned abatement
break-even price  = internal cost / planned abatement  (credits bought for the same quantity,
                    one credit per ton CO2e)
"""

from fractions import Fraction
import re

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h005"


def _utilization(text: str) -> Fraction:
    m = re.search(rf"utilization (?:of )?({NUMBER})\s*(percent|%)?", text)
    if m is None:
        raise ValueError("utilization not found")
    u = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        u /= 100
    return u


def solve(text: str, q: dict) -> dict:
    capacity = grab(r"abatement capacity (?:of )?(?:USD )?{N}\s*tons", text)
    util = _utilization(text)
    fixed = grab(r"Mobilizing internal abatement costs (?:USD )?{N}", text)
    var = grab(r"plus (?:USD )?{N}\s*(?:USD )?(?:for each|per) ton", text)

    planned = capacity * util
    internal_cost = fixed + var * planned
    price = internal_cost / planned

    return {"final": price, "slots": {"planned_abatement_checkpoint": planned}}
