"""h068 -- asset disposal: share of gross mechanical turnover uplift offset by sales-loss drag.

Pre-action base A0 = retained post-action base A1 + true reduction D.
Sales S0 fall by fraction g (stated as a plain ratio, e.g. 0.4 = 40%).
Gross mechanical uplift (asset-base reduction alone, sales held):  S0/A1 - S0/A0 = S0*D/(A0*A1)
Sales-loss drag (remaining step to the post-action state):        S0/A1 - S0*(1-g)/A1 = g*S0/A1
Offset share = drag / uplift = g*A0/D, reported in percent.
"""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h068"


def solve(text: str, q: dict) -> dict:
    a1 = grab(r"retains a net total-asset base of {N}", text)
    d = grab(r"{N} is the true reduction from the pre-action total-asset base", text)
    g = grab(r"net sales fall by {N}", text)

    a0 = a1 + d
    uplift_rel = Fraction(a0, 1) / a1 - 1          # (S0/A1 - S0/A0) / T0 = D/A1
    drag_rel = g * a0 / a1                         # (g*S0/A1) / T0
    offset_pct = drag_rel / uplift_rel * 100

    return {
        "final": offset_pct,
        "slots": {"pre_action_asset_base_checkpoint": a0},
    }
