"""h068 -- asset disposal: share of the gross mechanical turnover uplift offset by the sales-loss drag.

AMBIGUITY HUNT (resolutions recorded before coding)

Given per instance: post-action net total-asset base A1, "true reduction" R, sales fall f.

1. Pre-action asset base (checkpoint).  "49 is the true reduction from the pre-action total-asset
   base after accounting for any disposal proceeds retained or distributed" -> R is an ABSOLUTE
   amount already net of proceeds, so A0 = A1 + R.  Not a percent (no "percent" word; and a
   98 "percent" reduction with 99 remaining would give an absurd 4950 base).  Unit usd, 4 dp,
   rendered by the framework from the exact Fraction.

2. "Comparable run-rate net sales fall by 0.4" -- absolute or fraction?  Pre-action sales are
   NEVER given, and every candidate ratio drag/uplift is proportional to (sales fall)/(pre
   sales).  The answer is therefore only determinable if the fall is a FRACTION of pre-action
   sales (0.4 = 40 %).  No "percent" word appears, so it is a plain ratio, not 0.4 %.
   (Defensive: if a variant says "fall by N percent" we divide by 100.)

3. Which base does the drag sit on?  Two readings:
     (a) sequential / gross-to-net: uplift = S/A1 - S/A0 (asset base shrinks, sales held);
         drag = S/A1 - S(1-f)/A1 = fS/A1 (sales loss applied at the post-action base), so that
         gross uplift - drag = actual net change exactly.  offset = drag/uplift = f*A0/R.
     (b) each effect "alone" vs pre-action: drag = fS/A0 -> offset = f*A1/R (leaves an
         interaction term unexplained).
   Evidence for (a): the word "gross" implies a gross-vs-net reconciliation; "alone" is
   attached only to the asset-base reduction (counterfactual, "would create"), whereas the
   sales loss "creates" (actual) the drag; "offset" means the part of the gross uplift that is
   cancelled on the way to the actual result, i.e. (gross - net)/gross, which equals f*A0/R
   identically.  Under (b) instance 1 would report ~80 % offset while actual turnover FALLS
   (net < 0) -- internally inconsistent; under (a) it reports >100 %, matching the fact that
   the drag more than fully offsets the uplift.  -> Use (a).

4. Units of the answer: "percent" -> drag/uplift * 100, unrounded (framework rounds half-up 2 dp).
   Sales level S cancels, so no normalisation assumption leaks into the result.

5. No rounding anywhere inside the chain (nothing says a rounded figure is reused).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, F, NUMBER

TEMPLATE_ID = "h068"


def _sales_fall_fraction(text: str) -> Fraction:
    m = re.search(
        rf"net sales (?:fall|decline|drop|decrease)s? by ({NUMBER})\s*(percent|%)?",
        text,
        flags=re.S | re.I,
    )
    if m is None:
        raise ValueError("sales fall not found")
    val = F(m.group(1))
    if m.group(2):
        val = val / 100
    return val


def solve(text: str, q: dict) -> dict:
    # Post-action (retained) net total-asset base.
    a1 = grab(r"net total-asset base of {N}", text)
    # True (net-of-proceeds) absolute reduction from the pre-action base.
    r = grab(r"{N} is the true reduction from the pre-action total-asset base", text)
    # Sales fall as a fraction of pre-action run-rate net sales.
    f = _sales_fall_fraction(text)

    # Checkpoint: pre-action total-asset base.
    a0 = a1 + r

    # Work with pre-action sales normalised to 1 (it cancels in the ratio).
    s = Fraction(1)
    t0 = s / a0                 # pre-action turnover
    t_gross = s / a1            # asset-base reduction alone (sales held constant)
    t_net = s * (1 - f) / a1    # actual post-action turnover

    gross_uplift = t_gross - t0         # = s*r/(a0*a1)
    drag = t_gross - t_net              # = f*s/a1  (gross - drag == net change)

    offset_pct = drag / gross_uplift * 100   # == f*a0/r*100

    return {
        "final": offset_pct,
        "slots": {"pre_action_asset_base_checkpoint": a0},
    }
