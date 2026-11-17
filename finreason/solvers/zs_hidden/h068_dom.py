"""h068 -- asset-turnover bridge around an asset disposal (FINANCE MODEL FIRST).

MODEL
-----
Asset turnover  T = comparable run-rate net sales / total assets.

Given:
  A1 = net total-asset base retained AFTER the action.
  R  = the TRUE reduction from the pre-action total-asset base (the text says this
       already accounts for disposal proceeds retained or distributed, so no further
       cash adjustment is made).
  g  = fractional fall in comparable run-rate net sales ("fall by 0.4" -> 40% of the
       pre-action level).  Pre-action sales S0 is not given, so the quantity asked
       for must be (and is) independent of S0, which forces g to be a relative
       decline (S1 = S0 * (1 - g)).

Derived:
  A0 = A1 + R                         pre-action (comparable) total-asset base
       -> this is the checkpoint "pre_action_asset_base_checkpoint" (USD).

Standard two-factor turnover bridge (sales effect measured on the post-action
asset base so the two effects reconcile exactly to the total change):

  T0 = S0 / A0
  T1 = S1 / A1 = S0 (1 - g) / A1

  gross mechanical uplift (asset reduction alone, sales held at S0)
      U = S0/A1 - S0/A0 = S0 * R / (A0 * A1)
  sales-loss drag (sales fall evaluated on the post-action asset base)
      D = (S0 - S1) / A1 = g * S0 / A1
  check: U - D = T1 - T0   (exact reconciliation)

  Share of the gross uplift offset by the drag:
      D / U = g * A0 / R           -> times 100 for percent.
  (May exceed 100% when the sales loss more than wipes out the mechanical uplift.)

OVERRIDES / CONVENTIONS NOTED
  * No overrides of standard finance conventions in the text.
  * Result unit is percent (value 119.93 means 119.93%).
  * Everything exact (Fractions); no intermediate rounding.
"""
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h068"


def solve(text: str, q: dict) -> dict:
    a1 = grab(r"retains a net total-asset base of {N}", text)
    red = grab(r"while {N} is the true reduction", text)
    g = grab(r"net sales fall by {N}", text)

    a0 = a1 + red                      # pre-action total-asset base
    uplift_per_s0 = red / (a0 * a1)    # S0 * (1/A1 - 1/A0) with S0 = 1
    drag_per_s0 = g / a1               # g * S0 / A1 with S0 = 1
    final = drag_per_s0 / uplift_per_s0 * 100   # = 100 * g * A0 / R

    return {
        "final": final,
        "slots": {"pre_action_asset_base_checkpoint": a0},
    }
