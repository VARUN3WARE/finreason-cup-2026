from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h058"


def solve(text: str, q: dict) -> dict:
    # Primary review detects ratio p of the whole population.
    p = grab(r"primary review detects exact decimal ratio {N}", text)
    # Target unique combined detection ratio T.
    t = grab(r"target unique combined detection ratio is {N}", text)

    # Complement remaining after primary review (missed set), as a plain ratio.
    missed = 1 - p

    # Sequential, non-overlapping stages: combined = p + (1 - p) * b >= T
    # => b >= (T - p) / (1 - p). A conditional detection ratio cannot be
    # negative, so if the primary review already reaches the target the
    # minimum backup ratio is 0.
    if t <= p:
        b = Fraction(0)
    else:
        b = (t - p) / missed

    return {"final": b * 100, "slots": {"primary_miss_checkpoint": missed}}
