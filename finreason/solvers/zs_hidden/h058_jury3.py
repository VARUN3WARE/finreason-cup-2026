from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h058"


def solve(text: str, q: dict) -> dict:
    # primary detection ratio p, target unique combined ratio T (both exact ratios)
    p = grab(r"primary review detects exact decimal ratio\s+{N}", text)
    t = grab(r"target unique combined detection ratio is\s+{N}", text)

    # stage-1 complement: share of the population missed by the primary review
    miss = 1 - p

    # backup acts only on the missed set, detections are disjoint:
    #   T = p + (1 - p) * b   =>   b = (T - p) / (1 - p)
    # A conditional ratio cannot be negative: if the primary review already meets or
    # exceeds the target (T <= p), the minimum backup ratio required is 0.
    need = t - p
    if need <= 0:
        b = Fraction(0)
    else:
        b = need / miss

    return {
        "final": b * 100,  # percent
        "slots": {"primary_miss_checkpoint": miss},
    }
