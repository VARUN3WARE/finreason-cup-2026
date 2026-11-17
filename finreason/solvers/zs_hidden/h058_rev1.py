"""h058 (blind reviewer 1, upholds adjA) -- two-stage (primary + backup on missed set) detection: required backup conditional ratio.

Literal transcription:
  * primary review detects ratio p of the population.
  * backup review is applied only to the missed set (1 - p) and detects a conditional ratio b of it,
    so stages do not overlap: unique combined = p + (1 - p) * b   (no independence / inclusion-exclusion).
  * target unique combined ratio T.
  * minimum b so that p + (1 - p) * b >= T  ->  b = (T - p) / (1 - p), but a detection ratio cannot be
    negative: if the primary ratio already reaches the target (p >= T) the minimum backup ratio is 0.
  * checkpoint: complement ratio remaining after primary review = 1 - p.
  * final reported as a percentage.
"""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h058"


def solve(text: str, q: dict) -> dict:
    # "a primary review detects exact decimal ratio {p} of one fixed eligible transaction population"
    p = grab(r"primary review detects (?:exact decimal )?ratio {N}", text)
    # "The target unique combined detection ratio is {T}"
    T = grab(r"target unique combined detection ratio is {N}", text)

    # "A backup review is applied only to transactions missed by the primary review"
    missed = 1 - p  # complement remaining after primary review (checkpoint)

    # unique combined = p + missed * b  >= T
    if p >= T:
        b = Fraction(0)
    else:
        b = (T - p) / missed
    # a detection ratio cannot be negative (floor at zero)
    b = max(Fraction(0), b)

    final_pct = b * 100
    return {"final": final_pct, "slots": {"primary_miss_checkpoint": missed}}
