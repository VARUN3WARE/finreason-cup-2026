"""h105 -- social-impact program: beneficiary-equivalent scale meeting a surplus requirement.

Rules read from the text
------------------------
* combined fixed costs      = launch cost + monitoring cost
* required social value     = combined fixed costs * (1 + surplus ratio)   (stated explicitly)
* total social value        = scale * value per unit
* scale "exactly meets" the requirement  ->  scale = required social value / value per unit
  (plain division, no integer ceiling; the answer is a 2-dp decimal count)
* checkpoint "surplus requirement attributable to monitoring cost" (usd):
  the surplus requirement is the excess over fixed costs the investor demands,
  combined fixed costs * surplus ratio; the part attributable to the monitoring
  cost is monitoring cost * surplus ratio.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h105"


def solve(text: str, q: dict) -> dict:
    launch = grab(r"launch cost (?:of )?{N}", text)
    monitoring = grab(r"monitoring cost (?:of )?{N}", text)
    unit_value = grab(r"net monetized social value (?:of )?{N}", text)
    ratio = grab(r"surplus ratio (?:of )?{N}", text)

    combined_fixed = launch + monitoring
    required_value = combined_fixed * (1 + ratio)
    scale = required_value / unit_value

    monitoring_surplus = monitoring * ratio

    return {
        "final": scale,
        "slots": {"monitoring_surplus_value_checkpoint": monitoring_surplus},
    }
