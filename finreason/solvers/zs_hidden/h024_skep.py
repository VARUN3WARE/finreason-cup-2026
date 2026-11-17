"""h024 -- maximum preferred-dividend allocation per current common share that keeps
pro forma post-issuance EPS at or above a floor.

AMBIGUITY RESOLUTIONS (all from the question text):
1. "increases the common-share base by ratio r": the post-issuance share count is
   S * (1 + r). The *multiple* is therefore 1 + r, not r itself (r alone, e.g. 0.2,
   would be a decrease, contradicting "increases").
2. Checkpoint "post-issuance share-base multiple" (unit: multiple) = post shares /
   current shares = 1 + r. It is the share-count ratio, NOT its reciprocal (the EPS
   dilution factor 1/(1+r)). Returned unrounded; framework rounds to 6 dp half up.
3. "earnings normalized per current common share are E" is stated "Before preferred
   distributions and a planned common-share issuance", so E is pre-preferred earnings
   divided by the CURRENT share count. The issuance brings no extra earnings (none
   stated), so it is purely dilutive.
4. The preferred allocation P is "per current common share" (stated twice), so total
   preferred = P * S and total earnings = E * S. Pro forma post-issuance EPS =
   (E*S - P*S) / (S*(1+r)) = (E - P) / (1 + r); S cancels.
5. "at or above T" is non-strict, so the maximum P is attained at equality:
   (E - P)/(1+r) = T  ->  P = E - T*(1+r).
6. No zero floor is worded, so the raw value is returned (all three instances are
   positive, so this cannot change any answer).
7. Final answer unit is USD per current common share; framework rounds to 2 dp half up.
   Nothing in the text asks for intermediate rounding, so none is applied.
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h024"


def solve(text: str, q: dict) -> dict:
    # Pre-preferred, pre-issuance earnings per CURRENT common share (USD).
    e = grab(r"earnings normalized per current common share are\s*{N}", text)
    # Issuance ratio: new shares / current shares.
    r = grab(r"increases the common-share base by ratio\s*{N}", text)
    # EPS floor (non-strict: "at or above").
    t = grab(r"EPS\s+(?:at or above|at least|of at least|no lower than|not below)\s*{N}", text)

    # Post-issuance share-base multiple = post shares / current shares.
    multiple = Fraction(1) + r

    # (E - P) / multiple >= T  ->  P <= E - T * multiple ; maximum at equality.
    p_max = e - t * multiple

    return {
        "final": p_max,
        "slots": {"dilution_multiple_checkpoint": multiple},
    }
