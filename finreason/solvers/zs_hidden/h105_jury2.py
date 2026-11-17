from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h105"


def solve(text: str, q: dict) -> dict:
    launch = grab(r"launch cost {N}", text)
    monitoring = grab(r"monitoring cost {N}", text)
    value_per_unit = grab(r"net monetized social value {N}", text)
    ratio = grab(r"surplus ratio {N}", text)

    fixed = launch + monitoring
    required_value = fixed * (1 + ratio)
    scale = required_value / value_per_unit

    # Surplus (the amount above combined fixed costs) attributable to monitoring cost.
    monitoring_surplus = monitoring * ratio

    return {
        "final": scale,
        "slots": {"monitoring_surplus_value_checkpoint": monitoring_surplus},
    }
