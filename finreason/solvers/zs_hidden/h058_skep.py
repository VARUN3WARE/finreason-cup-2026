"""h058 -- two-stage (primary + backup) transaction review, required backup detection ratio.

Structure
---------
primary review detects ratio p of the population; the backup review is applied ONLY to the
missed set (1 - p) and detects a conditional ratio b of it, so the two detection sets are
disjoint:  unique combined detection = p + (1 - p) * b.
The target combined ratio T is reached when p + (1 - p) * b = T  ->  b = (T - p) / (1 - p).

Ambiguities hunted and resolved
-------------------------------
1. Combination rule: the text says the backup is applied only to transactions missed by the
   primary review, "so detections from the two stages do not overlap", and explicitly says
   "Do not assume independent detectors or apply inclusion-exclusion".  Hence the combined
   ratio is the plain sum p + (1-p)*b (the backup ratio is CONDITIONAL on the missed set, so
   it must be scaled by the complement 1-p, not added raw).  (Note: p + b - p*b under
   independence happens to give the same algebra, so this does not change the value anyway.)
2. "reaches the target": minimum b such that p + (1-p)*b >= T, i.e. the equality solution
   b = (T - p)/(1 - p).  No rounding before the final percentage ("exact arithmetic ...
   rounding only the final percentage").
3. Premise "with the primary ratio strictly below the target" vs the actual numbers: the three
   instances have p == T (twice) and p > T (once).  Two readings exist for p >= T:
     (a) raw closed form (T-p)/(1-p)  -> 0 when p == T, NEGATIVE when p > T;
     (b) floor at zero (no backup needed).
   Resolution: (a).  The text never says "floored at zero"/"larger of ... and zero", which this
   dataset family states explicitly whenever a floor is applied (cf. the quick-ratio / net-margin
   seen templates).  The strict-below premise is used *instead of* a floor, exactly like the
   sibling unseen clusters ("Assuming the target exceeds the post-downturn revenue, compute the
   required recovery rate ..."), whose closed forms are likewise unfloored.  The answer spec is a
   plain signed decimal percent, so a negative value is representable.  When p == T both
   readings agree (0.00), so only the p > T instance depends on this choice.
4. Units: inputs are plain ratios ("exact decimal ratio 0.5", "2/3", "ratio is 0.57325"); a
   defensive fallback treats a number immediately followed by "percent" as a percentage.
   The final answer is the backup ratio AS A PERCENTAGE (x100); the checkpoint is a RATIO.
5. Checkpoint primary_miss_checkpoint = "the complement ratio remaining after primary review"
   = 1 - p (ratio, unrounded; framework rounds half-up to 6 places, e.g. 1/3 -> 0.333333).
6. Division by zero (p == 1) cannot occur in these instances; raise a clear error if it does
   rather than silently returning something.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import F, NUMBER

TEMPLATE_ID = "h058"


def _ratio_after(text: str, patterns: list[str]) -> Fraction:
    """First pattern that matches; number followed by 'percent' is scaled to a ratio."""
    for pat in patterns:
        rx = pat.replace("{N}", f"({NUMBER})")
        m = re.search(rx, text, flags=re.S | re.I)
        if m is None:
            continue
        value = F(m.group(1))
        tail = text[m.end(1): m.end(1) + 12].lower()
        if tail.lstrip().startswith(("percent", "%", "per cent")):
            value = value / 100
        return value
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def solve(text: str, q: dict) -> dict:
    # primary detection ratio p
    p = _ratio_after(
        text,
        [
            r"primary review detects (?:an? )?(?:exact )?(?:decimal |rational |fractional )?ratio (?:of )?{N}",
            r"primary review detects (?:an? )?(?:exact )?(?:decimal |rational |fractional )?(?:share |proportion |fraction )?(?:of )?{N}",
            r"primary[^.]*?detects[^.]*?{N}",
        ],
    )
    # target unique combined detection ratio T
    t = _ratio_after(
        text,
        [
            r"target unique combined detection ratio is {N}",
            r"target[^.]*?combined[^.]*?ratio[^.]*?is {N}",
            r"target[^.]*?ratio[^.]*?is {N}",
        ],
    )

    miss = 1 - p  # complement ratio remaining after primary review
    if miss == 0:
        raise ValueError("primary review detects everything; backup ratio undefined")

    # unique combined = p + miss * b  ==  T   ->   b = (T - p) / miss   (unfloored, see note 3)
    backup = (t - p) / miss

    return {
        "final": backup * 100,  # percent
        "slots": {"primary_miss_checkpoint": miss},
    }
