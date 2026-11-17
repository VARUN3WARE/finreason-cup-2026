"""h018 -- three-stage financing: which option's pro forma EPS meets the floor.

AMBIGUITIES CONSIDERED AND HOW EACH WAS RESOLVED (textual evidence in quotes)
---------------------------------------------------------------------------
1. Is the per-stage "share-base increase" a ratio or a percent?
   -> Ratio. The text says "its cumulative share multiple is (1 + the ratio)^3"
      and the numbers (0.7, 0.8, 0.2345675) are plainly fractional ratios, not percents.
      No /100 is applied.

2. How does "adds total earnings of X per current share" enter the EPS?
   -> Normalize current shares to 1. Current earnings per current share = E0; added
      earnings per current share = X. Total pro forma earnings (per current share) = E0 + X,
      spread over the enlarged share base M = (1 + r)^3.
      Pro forma EPS = (E0 + X) / M.   (NOT E0/M + X: added earnings are also diluted,
      because EPS = total earnings / total shares.)

3. Strict vs non-strict floor?
   -> Non-strict. "requires pro forma EPS of at least <floor>" and "qualifies only if its
      exact pro forma EPS meets the floor" -> qualify iff EPS >= floor (exact Fractions).

4. Number of stages / exponent.
   -> "exactly three sequential ... stages" and "(1 + the ratio)^3". The exponent is parsed
      from the "^N" in the text for each option (fallback 3) rather than hard-coded.

5. Selection and tie rule.
   -> "select the qualifying option with the higher exact EPS, use `option_a` on an exact tie,
      and use `neither_option` if neither qualifies." Only qualifying options compete; if just
      one qualifies it is chosen regardless of the other's EPS; exact tie (both qualify) -> A.

6. Checkpoint "Option A share-base multiple after one issuance stage" (unit: multiple).
   -> The multiple after ONE stage is (1 + r_A)^1 = 1 + r_A (the "multiple", not the bare
      increase r_A, and not the cumulative three-stage multiple). Returned UNROUNDED; the
      framework applies half-up to 6 dp (e.g. 1.2345675 -> 1.234568).

7. Rounding inside the computation?
   -> None. "exact pro forma EPS" is explicitly demanded; everything stays in Fraction.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, F

TEMPLATE_ID = "h018"


def _exponent(text: str, anchor_pattern: str, default: int = 3) -> int:
    """Parse the integer exponent in '(1 + the ratio)^N' following the anchor; default 3."""
    m = re.search(anchor_pattern + r"\s*\(1\s*\+\s*the ratio\)\s*\^\s*(\d+)", text, flags=re.S)
    if m is None:
        return default
    return int(m.group(1))


def solve(text: str, q: dict) -> dict:
    # --- inputs -------------------------------------------------------------
    e0 = grab(r"current common EPS (?:of )?{N}", text)
    floor = grab(r"pro forma EPS of at least {N}", text)

    add_a = grab(r"Option A adds total earnings of {N} per current share", text)
    r_a = grab(r"per-stage share-base increase is {N}", text)

    add_b = grab(r"Option B analogously adds {N} per current share", text)
    r_b = grab(r"uses per-stage increase {N}", text)

    n_a = _exponent(text, r"cumulative share multiple is")
    n_b = _exponent(text, r"for cumulative multiple")

    # --- share-base multiples (exact integer powers) --------------------------
    one_stage_a = (1 + r_a) ** 1          # checkpoint: multiple after ONE stage
    mult_a = (1 + r_a) ** n_a
    mult_b = (1 + r_b) ** n_b

    # --- exact pro forma EPS ----------------------------------------------------
    eps_a = (e0 + add_a) / mult_a
    eps_b = (e0 + add_b) / mult_b

    # --- qualification: "at least" / "meets the floor" -> non-strict ------------
    qual_a = eps_a >= floor
    qual_b = eps_b >= floor

    if qual_a and qual_b:
        final = "option_a" if eps_a >= eps_b else "option_b"   # exact tie -> option_a
    elif qual_a:
        final = "option_a"
    elif qual_b:
        final = "option_b"
    else:
        final = "neither_option"

    return {
        "final": final,
        "slots": {
            "a_one_stage_share_multiple_checkpoint": one_stage_a,
        },
    }
