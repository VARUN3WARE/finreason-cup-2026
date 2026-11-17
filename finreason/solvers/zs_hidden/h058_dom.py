# FINANCE MODEL (h058): two-stage sequential detection, non-overlapping.
#   p  = primary detection ratio of the fixed eligible population (exact, given)
#   T  = target unique combined detection ratio (given)
#   b  = backup conditional detection ratio applied ONLY to the missed set (1 - p)
#   Unique combined detection = p + (1 - p) * b   (disjoint stages; no independence,
#   no inclusion-exclusion).
#   Solve p + (1-p) b >= T  ->  minimum b = (T - p) / (1 - p).
# Checkpoint "primary_miss_checkpoint" = complement ratio remaining after primary review = 1 - p
#   (plain ratio, 6 dp).
# Final = required backup ratio as a PERCENT = 100 * b_min.
# Override / branch handling: a conditional detection ratio cannot be negative. The text
#   asserts "primary strictly below target", but if p >= T the target is already met by the
#   primary review alone, so the minimum backup ratio needed is 0 (floored at zero) rather than
#   a negative number. If p < T the formula applies (b <= 1 whenever T <= 1).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h058"


def solve(text: str, q: dict) -> dict:
    p = grab(r"detects exact decimal ratio {N} of one fixed", text)
    t = grab(r"target unique combined detection ratio is {N}", text)
    miss = 1 - p
    if t <= p:
        b = Fraction(0)
    else:
        b = (t - p) / miss
    return {"final": b * 100, "slots": {"primary_miss_checkpoint": miss}}
