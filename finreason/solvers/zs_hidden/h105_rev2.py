"""Hidden cluster h105 -- social-impact program: beneficiary-equivalent scale meeting a surplus requirement.

Literal transcription, sentence by sentence:

S1 "A social-impact program has launch cost L and monitoring cost M."
S2 "Each beneficiary-equivalent unit is expected to create net monetized social value v."
S3 "The investor requires total social value, defined as beneficiary-equivalent scale multiplied by value
    per unit, to exceed the combined fixed costs by the surplus ratio s; equivalently, required social
    value is combined fixed costs multiplied by one plus that ratio."
      total_social_value(scale) = scale * v
      combined_fixed_costs      = L + M
      required surplus          = combined_fixed_costs * s     (the amount by which value must exceed costs)
      required_social_value     = combined_fixed_costs * (1 + s)
S4 "Compute the beneficiary-equivalent scale that exactly meets this requirement."
      scale * v = required_social_value  ->  scale = required_social_value / v   (exact, no whole-unit rounding)

Checkpoint (position 1) monitoring_surplus_value_checkpoint, "the surplus requirement attributable to
monitoring cost" (usd): the part of the required surplus that comes from the monitoring cost,
M * s, so that required surplus = L*s + M*s and required value = (L + M) + L*s + M*s.
"""

import re
from fractions import Fraction

from finreason.nums import NUMBER, grab

TEMPLATE_ID = "h105"


def solve(text: str, q: dict) -> dict:
    # S1: the two fixed cost components.
    launch_cost = grab(r"launch cost (?:of )?(?:USD )?{N}", text)
    monitoring_cost = grab(r"monitoring cost (?:of )?(?:USD )?{N}", text)

    # S2: net monetized social value created by each beneficiary-equivalent unit.
    value_per_unit = grab(r"net monetized social value (?:of )?(?:USD )?{N}", text)

    # S3: surplus ratio (a plain ratio, e.g. 0.1 = 10 percent above combined fixed costs).
    surplus_ratio = grab(r"surplus ratio (?:of )?{N}", text)
    if re.search(r"surplus ratio (?:of )?(?:" + NUMBER + r")\s*(?:percent|%)", text):
        surplus_ratio = surplus_ratio / 100  # defensive: only if the ratio were ever quoted in percent

    #     combined fixed costs = launch cost + monitoring cost
    combined_fixed_costs = launch_cost + monitoring_cost
    #     the requirement: value must exceed combined fixed costs by the surplus ratio
    required_surplus = combined_fixed_costs * surplus_ratio
    launch_surplus_value = launch_cost * surplus_ratio
    monitoring_surplus_value = monitoring_cost * surplus_ratio
    assert launch_surplus_value + monitoring_surplus_value == required_surplus
    #     equivalently: required social value = combined fixed costs * (1 + surplus ratio)
    required_social_value = combined_fixed_costs * (Fraction(1) + surplus_ratio)
    assert required_social_value == combined_fixed_costs + required_surplus

    # S4: total social value = scale * value per unit must exactly equal the required social value.
    if value_per_unit == 0:
        raise ValueError("value per unit is zero; scale undefined")
    scale = required_social_value / value_per_unit
    assert scale * value_per_unit == required_social_value

    return {
        "final": scale,
        "slots": {"monitoring_surplus_value_checkpoint": monitoring_surplus_value},
    }
