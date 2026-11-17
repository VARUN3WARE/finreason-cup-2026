from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h105"


def solve(text: str, q: dict) -> dict:
    launch = grab(r"launch cost\s+{N}", text)
    monitoring = grab(r"monitoring cost\s+{N}", text)
    value_per_unit = grab(r"net monetized social value\s+{N}", text)
    ratio = grab(r"surplus ratio\s+{N}", text)

    fixed = launch + monitoring
    required_value = fixed * (1 + ratio)          # total social value needed (exactly meets)
    scale = required_value / value_per_unit        # beneficiary-equivalent scale (count)

    # Surplus requirement attributable to monitoring cost = monitoring cost * surplus ratio (usd)
    monitoring_surplus = monitoring * ratio

    return {
        "final": scale,
        "slots": {"monitoring_surplus_value_checkpoint": monitoring_surplus},
    }
