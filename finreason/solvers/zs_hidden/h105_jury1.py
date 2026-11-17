from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h105"


def solve(text: str, q: dict) -> dict:
    launch = F(grab(r"launch cost {N}", text))
    monitoring = F(grab(r"monitoring cost {N}", text))
    value = F(grab(r"net monetized social value {N}", text))
    ratio = F(grab(r"surplus ratio {N}", text))

    fixed = launch + monitoring
    required = fixed * (1 + ratio)
    scale = required / value
    monitoring_surplus = monitoring * ratio

    return {"final": scale,
            "slots": {"monitoring_surplus_value_checkpoint": monitoring_surplus}}
