from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h058"


def solve(text: str, q: dict) -> dict:
    # Primary detects ratio p of the whole population.
    p = grab(r"primary review detects exact decimal ratio {N}", text)
    # Target unique combined detection ratio T.
    t = grab(r"target unique combined detection ratio is {N}", text)

    # Complement remaining after primary review (the missed set the backup sees).
    miss = 1 - p

    # Sequential, non-overlapping stages: combined = p + (1 - p) * b >= T.
    # Minimum b = (T - p) / (1 - p); a detection ratio cannot be negative, so when
    # the primary alone already meets the target the minimum required backup ratio is 0.
    if miss == 0:
        b = Fraction(0)
    else:
        b = (t - p) / miss
    if b < 0:
        b = Fraction(0)

    return {"final": b * 100, "slots": {"primary_miss_checkpoint": miss}}
