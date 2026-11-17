"""Cluster h012 -- whale-transfer excess with a concentration-selected threshold.

AMBIGUITIES CONSIDERED AND RESOLUTIONS (with textual evidence)
--------------------------------------------------------------
1. Haircut: "ratio" vs percent.
   Text: "reduced by haircut ratio 0.2499995 ... rolling threshold times
   (1-single-threshold haircut ratio)".  The number is already a plain ratio
   (0.2, 0.25, 0.3) -> used as-is, NOT divided by 100.

2. Direction of the haircut (multiply by h or by 1-h).
   Text gives the formula explicitly: single threshold = rolling * (1 - h).
   Retained fraction = 1 - h.

3. Checkpoint "single_threshold_retention_checkpoint" (unit ratio, 6 dp):
   "the retained fraction used to derive the concentrated-transfer threshold".
   That is (1 - h) itself -- a dimensionless ratio, NOT the USD single
   threshold and NOT the haircut h.  Returned unrounded (framework rounds).

4. Concentration denominator: "total activity" vs the three-transfer sum.
   Text: "Compute current-transfer concentration as current transfer divided
   by total activity."  Total activity is the separately stated figure
   ("total activity over the monitoring horizon, including all three
   transfers, is X USD"), which in every instance EXCEEDS the sum of the three
   transfers (e.g. 1314 vs 885+102+204=1191).  So the denominator is the
   stated total-activity number, not the recomputed sum.

5. Branch comparison: "If it is at least 0.65, including exact equality"
   -> concentration >= cutoff (non-strict).  Exact Fraction comparison.

6. Fallback branch base: "the three-transfer total's excess over the
   unadjusted rolling threshold".  "Three-transfer total" = current + the two
   prior transfers (the sum of exactly those three transfers), which is a
   different quantity from "total activity" (the text deliberately uses two
   different names, and the figures differ).  Threshold here is the
   UNADJUSTED rolling threshold (no haircut).

7. Concentrated branch: excess = current transfer - haircut-adjusted single
   threshold.  Only the current transfer, not the total.

8. Floor at zero / sign: no floor is worded ("excess over" is a plain
   difference), so the signed difference is returned.  All three instances
   are positive anyway.

9. Rounding: "Use exact arithmetic for threshold adjustment, concentration,
   and branch selection, and round only the final USD excess half up to two
   decimal places."  -> no intermediate rounding anywhere; the framework
   applies the final half-up rounding.  (Instance with excess 112.175 is a
   half-up tie -> 112.18; instance with 151.499511 tests exact threshold.)

10. Prior transfers are only used in the fallback branch (three-transfer
    total); they are not part of the concentration numerator.
"""

from fractions import Fraction

from finreason.nums import grab, grab_all, F  # noqa: F401

TEMPLATE_ID = "h012"


def solve(text: str, q: dict) -> dict:
    # --- parse (anchored on surrounding words) ---
    current = grab(r"current transfer of {N} USD", text)
    prior1, prior2 = grab_all(r"prior transfers of {N} USD and {N} USD", text)
    rolling = grab(r"rolling-window whale threshold is {N} USD", text)
    haircut = grab(r"haircut ratio {N}", text)
    total_activity = grab(
        r"total activity over the monitoring horizon[^.]*?is {N} USD", text
    )
    cutoff = grab(r"If it is at least {N}", text)

    # --- threshold adjustment (exact) ---
    retained = Fraction(1) - haircut                 # retained fraction (ratio)
    single_threshold = rolling * retained            # haircut-adjusted, USD

    # --- concentration and branch selection (exact) ---
    concentration = current / total_activity
    if concentration >= cutoff:                      # "at least ... including exact equality"
        excess = current - single_threshold
    else:
        three_total = current + prior1 + prior2      # the three-transfer total
        excess = three_total - rolling               # unadjusted rolling threshold

    return {
        "final": excess,
        "slots": {"single_threshold_retention_checkpoint": retained},
    }
