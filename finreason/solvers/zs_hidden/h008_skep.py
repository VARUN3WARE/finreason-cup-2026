"""h008 -- implied residual (salvage) value under straight-line depreciation.

Question structure
------------------
  "An asset has original cost C in USD millions. Under straight-line depreciation,
   f of its depreciable life has elapsed. Determine the residual value that would
   produce a target carrying amount CA at that point."

Straight-line: accumulated depreciation after fraction f of the life has elapsed is
    AccDep = f * (C - R)                       (R = residual value)
Carrying amount at that point:
    CA = C - AccDep  =>  AccDep = C - CA
Solving for R:
    C - R = (C - CA) / f   =>   R = C - (C - CA) / f

Ambiguities considered and how they were resolved
--------------------------------------------------
1. "0.75 of its depreciable life has elapsed": the number is a FRACTION of the life
   (it says "0.75 of", not "0.75 percent of"). We still tolerate an explicit
   "percent"/"%" suffix defensively (then divide by 100), but none of the three
   instances uses it.
2. Checkpoint `implied_depreciation_checkpoint` is described as "Recover accumulated
   depreciation from cost and target carrying amount" -> it is C - CA (USD millions),
   the accumulated depreciation to date. It is NOT the total depreciable base (C - R)
   and NOT the per-period charge.
3. "Carrying amount" = cost - accumulated depreciation (no impairment/revaluation is
   mentioned, so nothing else enters).
4. Sign: the text never floors the residual value at zero, so the exact algebraic
   result is returned (sign preserved). All three instances are positive anyway.
5. Rounding: nothing in the text says any intermediate value is rounded before use,
   so every value is exact Fraction; the framework rounds half-up to 2 dp.
   (Instance 3 lands exactly on 19.135 -> 19.14, where float arithmetic could slip.)
6. Units: all inputs are stated in USD millions and both result specs are usd_million,
   so no scaling is needed.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h008"


def _fraction_elapsed(text: str) -> Fraction:
    """Fraction of the depreciable life that has elapsed (plain ratio)."""
    rx = rf"({NUMBER})\s*(percent|%)?\s*of\s+(?:its|the)\s+depreciable\s+life"
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError("fraction of depreciable life not found")
    val = F(m.group(1))
    if m.group(2):
        val = val / 100
    return val


def solve(text: str, q: dict) -> dict:
    cost = grab(r"original cost (?:of )?{N}", text)
    frac = _fraction_elapsed(text)
    target_ca = grab(r"target carrying amount of {N}", text)

    # Checkpoint: accumulated depreciation implied by cost and target carrying amount.
    acc_dep = cost - target_ca

    # Total depreciable base (cost - residual) consistent with f of the life elapsed.
    if frac == 0:
        raise ValueError("zero fraction of life elapsed: residual value is undetermined")
    depreciable_base = acc_dep / frac

    residual = cost - depreciable_base

    return {
        "final": residual,
        "slots": {"implied_depreciation_checkpoint": acc_dep},
    }
