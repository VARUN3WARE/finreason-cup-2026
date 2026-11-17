"""h068 -- asset disposal: share of gross mechanical turnover uplift offset by sales-loss drag.

Literal transcription:
  - post-action retained net total-asset base A1
  - true reduction from the pre-action base R  ->  pre-action comparable base A0 = A1 + R
  - comparable run-rate net sales fall by f (a fractional decline; no absolute sales level is
    given, so the decline is proportional: S1 = S0 * (1 - f))
  - pre-action turnover T0 = S0 / A0
  - gross mechanical uplift (asset reduction alone, sales held at S0): S0/A1 - S0/A0
  - sales-loss drag (at the post-action base): S0/A1 - S1/A1 = f * S0 / A1
  - offset share (percent) = drag / uplift * 100   (S0 cancels)
"""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h068"


def _sales_fall(text: str) -> Fraction:
    try:
        return grab(r"net sales fall by {N}\s*percent", text) / 100
    except ValueError:
        pass
    try:
        return grab(r"net sales fall by {N}\s*%", text) / 100
    except ValueError:
        pass
    return grab(r"net sales fall by {N}", text)


def solve(text: str, q: dict) -> dict:
    # "After the action it retains a net total-asset base of A1"
    a1 = grab(r"retains a net total-asset base of (?:USD\s*)?{N}", text)
    # "while R is the true reduction from the pre-action total-asset base ..."
    red = grab(r"{N} is the true reduction from the pre-action total-asset base", text)
    # comparable pre-action total-asset base
    a0 = a1 + red
    # "Comparable run-rate net sales fall by f"
    f = _sales_fall(text)

    # Normalise pre-action sales to 1 (S0 cancels out of the ratio).
    s0 = Fraction(1)
    s1 = s0 * (1 - f)
    t0 = s0 / a0                      # pre-action asset turnover
    t_assets_only = s0 / a1           # asset-base reduction alone
    t1 = s1 / a1                      # post-action turnover
    uplift = t_assets_only - t0       # gross mechanical turnover uplift
    drag = t_assets_only - t1         # turnover drag from sales loss
    offset_pct = drag / uplift * 100

    return {
        "final": offset_pct,
        "slots": {"pre_action_asset_base_checkpoint": a0},
    }
