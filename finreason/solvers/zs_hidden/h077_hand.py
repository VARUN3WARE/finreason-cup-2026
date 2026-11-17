from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h077"


def solve(text: str, q: dict) -> dict:
    in1 = grab(r"Period one has cash inflow {N}", text)
    out1 = grab(r"Period one has cash inflow [^ ]+ and cash outflow {N}", text)
    in2 = grab(r"Period two (?:then )?has cash inflow {N}", text)
    out2 = grab(r"Period two (?:then )?has cash inflow [^ ]+ and cash outflow {N}", text)
    floor = grab(r"must be at least {N}", text)

    net1 = in1 - out1
    net2 = in2 - out2

    # Opening cash O must satisfy O + net1 >= floor and O + net1 + net2 >= floor.
    req1 = floor - net1
    req2 = floor - (net1 + net2)
    opening = max(req1, req2)

    return {
        "final": Fraction(opening),
        "slots": {
            "period_one_net_to_floor_ratio_checkpoint": Fraction(net1) / floor,
        },
    }
