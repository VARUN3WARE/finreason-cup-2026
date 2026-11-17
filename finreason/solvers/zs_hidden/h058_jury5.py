"""h058 -- two-stage (primary + backup) detection, backup applied only to the
primary's misses, so unique combined detection = p + (1 - p) * b.

Required backup conditional ratio b = (T - p) / (1 - p).
A detection ratio cannot be negative, so when the primary already meets or
exceeds the target (p >= T, which is the case in every hidden instance even
though the text asserts p < T) the minimum backup ratio is 0.

Checkpoint ``primary_miss_checkpoint`` = complement left after primary = 1 - p
(plain ratio).  Final answer is b in percent.
"""

from fractions import Fraction

from finreason.nums import after

TEMPLATE_ID = "h058"


def solve(text: str, q: dict) -> dict:
    p = after(text, "detects exact decimal ratio")           # primary detection ratio of population
    target = after(text, "combined detection ratio is")      # target unique combined ratio

    miss = 1 - p                                             # share left for the backup stage

    if miss > 0:
        b = (target - p) / miss
    else:
        # primary catches everything; nothing left for backup, target already met
        b = Fraction(0)

    # a conditional detection ratio cannot be negative: if the primary alone
    # already reaches the target, the minimum backup ratio required is 0
    if b < 0:
        b = Fraction(0)

    return {
        "final": b * 100,                                    # percent
        "slots": {"primary_miss_checkpoint": miss},          # ratio
    }
