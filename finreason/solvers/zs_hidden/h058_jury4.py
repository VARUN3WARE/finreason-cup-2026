from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h058"


def solve(text: str, q: dict) -> dict:
    # primary detection ratio p, target unique combined ratio T
    p = grab(r"primary review detects exact decimal ratio\s+{N}\s+of", text)
    t = grab(r"target unique combined detection ratio is\s+{N}\s*,", text)

    # stage 1 leaves the complement; stage 2 detects conditional ratio b of it
    # (disjoint detections): p + (1 - p) * b = T  ->  b = (T - p) / (1 - p)
    miss = 1 - p
    b = (t - p) / miss
    # a ratio cannot be negative: if the primary alone already meets/exceeds the
    # target, the minimum backup ratio needed is 0
    if b < 0:
        b = Fraction(0)
    if b > 1:
        b = Fraction(1)
    return {
        "final": b * 100,
        "slots": {"primary_miss_checkpoint": miss},
    }
