"""Juror 5 solver for cluster h105: social-impact break-even scale with surplus ratio.

Hand solution, instance 1 (launch 147, monitoring 99, value/unit 59358/4001, ratio 0.1):
    combined fixed costs      = 147 + 99 = 246
    required social value     = 246 * (1 + 1/10) = 270.6
    scale (final, count)      = 270.6 / (59358/4001) = 1804451/98930 = 18.2397... -> 18.24
    slot monitoring_surplus_value_checkpoint (usd)
        = surplus requirement attributable to monitoring cost
        = monitoring cost * surplus ratio = 99 * 1/10 = 9.9 -> 9.90
      (alternative reading, monitoring cost grossed up: 99 * 1.1 = 108.9)
"""

from fractions import Fraction

from finreason.nums import grab, F  # noqa: F401

TEMPLATE_ID = "h105"


def solve(text: str, q: dict) -> dict:
    launch = grab(r"launch cost\s+{N}", text)
    monitoring = grab(r"monitoring cost\s+{N}", text)
    value_per_unit = grab(r"net monetized social value\s+{N}", text)
    ratio = grab(r"surplus ratio\s+{N}", text)

    fixed_costs = launch + monitoring
    # Required social value = combined fixed costs * (1 + surplus ratio), per the text.
    required_value = fixed_costs * (1 + ratio)
    # Beneficiary-equivalent scale that exactly meets the requirement (count, unrounded).
    scale = required_value / value_per_unit

    # Surplus requirement attributable to monitoring cost: the extra value (over and above
    # the monitoring cost itself) the surplus ratio demands on that cost item, in usd.
    monitoring_surplus_value = monitoring * ratio

    return {
        "final": Fraction(scale),
        "slots": {"monitoring_surplus_value_checkpoint": Fraction(monitoring_surplus_value)},
    }
