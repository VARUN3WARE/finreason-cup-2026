"""h053 -- percentage-scaled HHI-style concentration of modeled exposures.

AMBIGUITY RESOLUTIONS (skeptical pass):
1. "decimal assessment ratio 0.5" -- the word "decimal" makes it a plain multiplier,
   so P_i = volume * ratio with NO /100.  Guard: if the word "percent" immediately
   follows the ratio number in some instance, divide by 100.
2. Checkpoints "category_k modeled exposure before normalization" are P_k =
   volume_k * ratio_k in USD, i.e. BEFORE dividing by the total (the share s_k is
   the normalized quantity).  They are not shares and not squared shares.
3. Shares use the total of the EXPOSURES (sum of P_i), as the text defines s_i,
   not the total of volumes.
4. Final answer: "Report 100H as a percentage" and the answer unit is `percent`,
   so the returned value is 100 * H (38.08 means 38.08%), not H itself.
5. Rounding: only the final percentage is rounded (half-up, 2 dp) and the
   framework does that; every intermediate is an exact Fraction.
6. Parsing: the boilerplate "at least 33 1/3 percent" would pollute a naive
   number scan, so each category is anchored on "Category k has" and the next two
   numbers after that anchor are taken (volume first, "USD" must follow it, then
   the ratio).  All categories found are used (the text says exactly three).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER_RE, F

TEMPLATE_ID = "h053"

_CAT_RE = re.compile(r"Category\s+(\d+)\s+has\b", flags=re.I)


def _parse_categories(text: str) -> dict[int, tuple[Fraction, Fraction]]:
    """Return {k: (volume_usd, ratio)} for every 'Category k has ...' clause."""
    anchors = list(_CAT_RE.finditer(text))
    if not anchors:
        raise ValueError("no 'Category k has' clauses found")
    cats: dict[int, tuple[Fraction, Fraction]] = {}
    for idx, m in enumerate(anchors):
        k = int(m.group(1))
        seg_start = m.end()
        seg_end = anchors[idx + 1].start() if idx + 1 < len(anchors) else len(text)
        segment = text[seg_start:seg_end]
        nums = list(NUMBER_RE.finditer(segment))
        if len(nums) < 2:
            raise ValueError(f"category {k}: expected volume and ratio, got {len(nums)} numbers")
        vol_m, ratio_m = nums[0], nums[1]
        # Sanity: the volume should be followed by "USD" before the ratio number.
        between = segment[vol_m.end():ratio_m.start()]
        if "USD" not in between.upper():
            raise ValueError(f"category {k}: could not confirm USD volume")
        volume = F(vol_m.group(0))
        ratio = F(ratio_m.group(0))
        # Guard: a ratio stated in percent (not the case in the shown instances).
        tail = segment[ratio_m.end():ratio_m.end() + 12].lower()
        if re.match(r"\s*(percent|%)", tail):
            ratio = ratio / 100
        if k in cats:
            raise ValueError(f"duplicate category {k}")
        cats[k] = (volume, ratio)
    return cats


def solve(text: str, q: dict) -> dict:
    cats = _parse_categories(text)
    if 1 not in cats or 2 not in cats:
        raise ValueError("categories 1 and 2 are required for the checkpoints")

    # Modeled exposure before normalization: P_i = volume_i * ratio_i (USD).
    exposures = {k: v * r for k, (v, r) in cats.items()}
    total = sum(exposures.values(), Fraction(0))
    if total <= 0:
        raise ValueError("non-positive total exposure")

    # Shares of the exposure pool and the HHI-style sum of squared shares.
    shares = {k: p / total for k, p in exposures.items()}
    h = sum((s * s for s in shares.values()), Fraction(0))

    # "Report 100H as a percentage": answer unit is percent.
    final = 100 * h

    return {
        "final": final,
        "slots": {
            "category_1_exposure_checkpoint": exposures[1],
            "category_2_exposure_checkpoint": exposures[2],
        },
    }
