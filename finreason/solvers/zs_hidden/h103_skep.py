"""h103 -- fictional transaction-review policy (aggregate volume + spike ratio + critical flags).

AMBIGUITY RESOLUTIONS (skeptic pass):

1. Checkpoint quantity. Slot description: "the threshold fraction retained after one stage",
   unit "ratio"; text: "the one-stage threshold-retention factor". A *fraction retained* is
   dimensionless, so the checkpoint is (1 - f) for ONE stage -- not the three-stage product
   (1 - f)**3, and not the baseline threshold times (1 - f) (that would carry the threshold's
   unit, not be a "fraction"). Returned exact; the framework rounds half-up to 6 places
   (instance with f = 0.1999995 is a deliberate half-up tie: 0.8000005 -> 0.800001).

2. Reduction mechanics. "reduce the surviving spike threshold by fraction f of its then-current
   value ... no replenishment ... the effective threshold is the baseline multiplied by one
   minus that fraction three successive times" => effective = S0 * (1 - f)**3 (multiplicative,
   compounding), not S0 * (1 - 3f) (additive) and not S0 - 3*f*S0.

3. Aggregate volume = sum of the three related transactions (the "aggregate" of the listed
   cash transactions). Comparison is STRICT: sum > aggregate threshold.

4. Spike ratio = largest transaction / historical average (explicitly defined). Comparison is
   STRICT: ratio > effective threshold. Ties -> condition fails -> (absent flags) Standard review.

5. Logic: Enhanced review when (volume cond AND spike cond) OR flag1 OR flag2. "either critical
   flag is true" = logical OR of the two recorded booleans. Otherwise Standard review.
   The flags are "The policy also records X and Y." with X, Y in {true, false}.

6. Baseline spike threshold is a plain ratio (largest-to-history), fraction f is a plain
   fraction (not percent) -- no /100 anywhere.

7. Enum tokens must be exact and case-sensitive: "Enhanced review" / "Standard review".
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h103"


def solve(text: str, q: dict) -> dict:
    # --- parse inputs (anchored on surrounding words; nothing hardcoded) ---
    txns = grab_all(r"cash transactions are {N}, {N}, and {N}", text)
    assert len(txns) == 3
    agg_threshold = grab(r"aggregate review threshold is {N}", text)
    hist_avg = grab(r"historical average cash transaction is {N}", text)
    base_spike = grab(r"spike-ratio threshold is {N}", text)
    frac = grab(r"reduce the surviving spike threshold by fraction {N} of its then-current value", text)

    m = re.search(r"records (true|false) and (true|false)", text)
    if m is None:
        raise ValueError("critical flags not found")
    flag1 = m.group(1) == "true"
    flag2 = m.group(2) == "true"

    # --- computation (exact) ---
    retention_one_stage = Fraction(1) - frac               # checkpoint: fraction retained per stage
    effective_threshold = base_spike * retention_one_stage ** 3   # three successive stages

    aggregate_volume = sum(txns, Fraction(0))
    largest = max(txns)
    spike_ratio = largest / hist_avg

    volume_cond = aggregate_volume > agg_threshold          # strictly exceeds
    spike_cond = spike_ratio > effective_threshold          # strictly exceeds

    if (volume_cond and spike_cond) or flag1 or flag2:
        route = "Enhanced review"
    else:
        route = "Standard review"

    return {
        "final": route,
        "slots": {
            "spike_threshold_residual_factor_checkpoint": retention_one_stage,
        },
    }
