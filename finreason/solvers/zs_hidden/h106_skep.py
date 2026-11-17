"""h106 -- order of two actions (capex vs asset reduction) and two-period asset turnover.

AMBIGUITY HUNT (skeptic pass) -- every point where two analysts could disagree,
with the textual evidence used to resolve it:

A1. Which number is the pre-action base?
    "<R> is the net total-asset base that REMAINS AFTER a true reduction of <D>"
    -> R is the retained (post-reduction) base, D the amount removed.  "true
    reduction" = the base genuinely shrinks by D, so the pre-action base is
    A0 = R + D.  (Not: R is pre-action and R - D is retained.)

A2. "raises run-rate net sales by 0.5" / "lowers ... by 0.2": fraction, percent
    points or absolute USD?  No baseline sales amount is given anywhere, so the
    effects cannot be absolute; there is no "percent" word, so they are plain
    fractional rates -> multiplicative factors (1 + 0.5) = 1.5 and (1 - 0.2) = 0.8.
    The checkpoint is called a "sales factor" with unit "multiple", consistent.

A3. Compound vs additive: "the two sales effects compound" -> multiplicative,
    period-two factor = 1.5 * 0.8 = 1.2 (NOT 1 + 0.5 - 0.2 = 1.3).  It is the same
    in both orders, hence "common".

A4. Timing inside the periods: "each effect begins at its action date, persists".
    The asset sentences already include the FIRST action's asset change in
    period-one assets and the SECOND action's in period-two assets, so action
    dates are the start of period one and the start of period two.  Hence the
    period-one run-rate sales factor is the first action's factor alone and the
    period-two factor is the product of both.  No partial-period proration.

A5. Turnover per order: "arithmetic mean of the two period run-rate sales amounts
    divided by the arithmetic mean of the two period asset bases, equivalently
    their sums divided by their sums" -> (S1 + S2) / (A1 + A2).  Identical either
    way (equal-length periods), no ambiguity.

A6. Normalization: "normalize this turnover by the common pre-action turnover"
    -> divide by S0 / A0 with A0 = pre-action base = R + D (the base before either
    action) and S0 = baseline sales.  S0 cancels exactly:
        N_order = (f1 + f2) * A0 / (A1 + A2).

A7. Asset bases per order (verbatim from the text):
      capex-first:     A1 = A0 + C = R + D + C ("pre-action base plus the addition"),
                       A2 = R + C      ("retained base plus the addition")
      reduction-first: A1 = R          ("retained base"),
                       A2 = R + C      ("same final retained-plus-addition base")
    Note capex-first period one uses the PRE-ACTION base, not the retained base.

A8. Final quantity: "reduction-first normalized factor minus the capex-first
    normalized factor, expressed as a percentage of baseline turnover".  Both
    factors are already ratios to baseline turnover, so the answer is
    (N_red - N_capex) * 100 in percent.  The sign is preserved (it is negative in
    all three instances); no absolute value.

A9. Rounding: nothing in the text says a rounded or whole-unit value is reused, so
    all values are exact Fractions; the framework rounds the final (2 dp) and the
    checkpoints (6 dp / 4 dp) independently.

A10. Checkpoints:
    combined_sales_effect_checkpoint      = f_up * f_down            (period-two sales factor, multiple)
    shared_second_period_asset_base_checkpoint = R + C               (period-two total assets, USD)
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab, grab_all

TEMPLATE_ID = "h106"

_RAISE_VERBS = {"raises", "raise", "increases", "increase", "lifts", "lift", "boosts", "boost", "grows", "adds"}
_LOWER_VERBS = {"lowers", "lower", "reduces", "reduce", "cuts", "cut", "decreases", "decrease", "shrinks", "trims"}


def _sales_factor(subject_pattern: str, text: str) -> Fraction:
    """Multiplicative run-rate sales factor for '<subject> <verb> run-rate net sales by <x>'."""
    m = re.search(
        rf"{subject_pattern}\s+([A-Za-z]+)\s+run-rate net sales by\s+({NUMBER})",
        text,
        flags=re.S,
    )
    if m is None:
        raise ValueError(f"sales effect not found for {subject_pattern!r}")
    verb = m.group(1).lower()
    x = F(m.group(2))
    if verb in _RAISE_VERBS:
        return 1 + x
    if verb in _LOWER_VERBS:
        return 1 - x
    raise ValueError(f"unrecognised sales verb {verb!r}")


def solve(text: str, q: dict) -> dict:
    # --- parse (A1): retained base R and the true reduction D; pre-action base A0 = R + D
    retained, reduction = grab_all(
        r"{N} is the net total-asset base that remains after a true reduction of {N}", text
    )
    # net capitalized addition C of the modernization program
    addition = grab(r"{N} is the modernization program.s net capitalized addition to total assets", text)

    pre_action_base = retained + reduction  # A0

    # --- sales factors (A2): modernization raises by f, reduction lowers by g
    f_modern = _sales_factor(r"Modernization", text)   # 1 + 0.5
    f_reduce = _sales_factor(r"the reduction", text)   # 1 - 0.2

    # --- period-two (both actions) sales factor, common to both orders (A3)
    f_both = f_modern * f_reduce

    # --- period-two asset base, common to both orders (A7)
    final_base = retained + addition

    # --- capex-first order (A4, A7): period one = modernization only
    capex_sales_sum = f_modern + f_both                      # in units of baseline sales S0
    capex_asset_sum = (pre_action_base + addition) + final_base
    capex_norm = capex_sales_sum * pre_action_base / capex_asset_sum   # (A5, A6)

    # --- reduction-first order (A4, A7): period one = reduction only
    red_sales_sum = f_reduce + f_both
    red_asset_sum = retained + final_base
    red_norm = red_sales_sum * pre_action_base / red_asset_sum

    # --- final (A8): difference of normalized factors, in percent of baseline turnover
    final = (red_norm - capex_norm) * 100

    return {
        "final": final,
        "slots": {
            "combined_sales_effect_checkpoint": f_both,
            "shared_second_period_asset_base_checkpoint": final_base,
        },
    }
