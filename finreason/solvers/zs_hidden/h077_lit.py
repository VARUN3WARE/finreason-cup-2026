"""h077 -- minimum opening cash meeting two sequential period-end cash floors.

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h077"


def solve(text: str, q: dict) -> dict:
    # "Its unknown opening cash is carried through both periods."  -> C (unknown)
    # "Period one has cash inflow X and cash outflow Y."
    in1 = grab(r"Period one has cash inflow {N}", text)
    out1 = grab(r"Period one has cash inflow [^ ]+ and cash outflow {N}", text)
    # "Period two then has cash inflow X and cash outflow Y."
    in2 = grab(r"Period two then has cash inflow {N}", text)
    out2 = grab(r"Period two then has cash inflow [^ ]+ and cash outflow {N}", text)
    # "Each period-end cash balance must be at least F."
    floor = grab(r"period-end cash balance must be at least {N}", text)

    # Net cash flow of each period (all flows occur before the period end).
    net1 = in1 - out1
    net2 = in2 - out2

    # End1 = C + net1 >= floor ; End2 = C + net1 + net2 >= floor.
    req_from_p1 = floor - net1
    req_from_p2 = floor - net1 - net2
    min_opening = max(req_from_p1, req_from_p2)
    # Opening cash cannot be negative (never binds for this cluster's data).
    if min_opening < 0:
        min_opening = Fraction(0)

    # Checkpoint: period-one net cash flow as a fraction of the required floor.
    ratio = net1 / floor

    return {
        "final": min_opening,
        "slots": {"period_one_net_to_floor_ratio_checkpoint": ratio},
    }
