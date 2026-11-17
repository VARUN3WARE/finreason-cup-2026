from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h105"


def solve(text: str, q: dict) -> dict:
    launch = grab(r"launch cost {N}", text)
    monitoring = grab(r"monitoring cost {N}", text)
    value = grab(r"net monetized social value {N}", text)
    ratio = grab(r"surplus ratio {N}", text)

    fixed = launch + monitoring
    required = fixed * (1 + ratio)       # required total social value
    scale = required / value             # beneficiary-equivalent scale (count)

    # Surplus requirement = ratio * combined fixed costs; the monitoring-cost share is ratio * monitoring.
    monitoring_surplus = ratio * monitoring

    return {
        "final": scale,
        "slots": {"monitoring_surplus_value_checkpoint": monitoring_surplus},
    }
