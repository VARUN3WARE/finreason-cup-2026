"""h058 -- two-stage (primary + backup) transaction review, required backup ratio.

Structure of every instance:
  * primary review detects ratio p of a fixed population;
  * backup review is applied ONLY to the (1 - p) missed set and detects a
    conditional ratio b of it, so the two stages never overlap (no
    inclusion-exclusion, no independence assumption);
  * unique combined detection = p + (1 - p) * b;
  * target combined ratio T; question asks the MINIMUM b such that
    p + (1 - p) * b >= T.

Solving: b* = (T - p) / (1 - p).  A detection ratio is a proportion in [0, 1],
so when the primary stage alone already reaches/exceeds the target (T <= p,
which is what all three instances actually contain despite the text asserting
"primary strictly below target") the minimum required backup ratio is 0, not a
negative number.  We therefore clamp at 0.

Slot ``primary_miss_checkpoint``: the complement ratio remaining after the
primary review, i.e. the missed share (1 - p), as a plain ratio.

Final answer: required backup ratio in PERCENT (framework rounds half-up to 2dp).
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h058"


def solve(text: str, q: dict) -> dict:
    # primary detection ratio p (given as an exact decimal or simple fraction)
    p = grab(r"primary review detects exact decimal ratio\s+{N}", text)
    # target unique combined detection ratio T
    T = grab(r"target unique combined detection ratio is\s+{N}", text)

    one = Fraction(1)
    missed = one - p  # share of the population the backup review is applied to

    if missed == 0:
        # degenerate: primary catches everything; backup has nothing to review
        b = Fraction(0)
    else:
        b = (T - p) / missed
        # a conditional detection ratio cannot be negative; if the primary stage
        # already reaches the target, the minimum required backup ratio is 0
        if b < 0:
            b = Fraction(0)

    return {
        "final": b * 100,  # percent
        "slots": {"primary_miss_checkpoint": missed},
    }
