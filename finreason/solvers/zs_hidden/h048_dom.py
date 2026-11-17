# FINANCE MODEL (written before coding)
#
# Quantity: required recovery rate after a revenue downturn.
#
#   R0  = starting revenue (USD)
#   d   = "downturn ratio" -- the fraction of revenue LOST in the downturn
#         (a decline ratio / drawdown fraction, as in "downturn ratio 0.5" = a 50% fall).
#   R1  = post-downturn revenue = R0 * (1 - d)                    [checkpoint, USD]
#   T   = target revenue after recovery (USD), assumed T > R1
#   g   = required recovery rate = (T - R1) / R1                  [final, reported as percent]
#       = (T / R1 - 1) * 100 %
#
# Convention / interpretation notes:
#   * "downturn ratio" is read as the fractional decline (loss), so R1 = R0 * (1 - d).
#     For d = 0.5 both readings (keep 50% vs lose 50%) coincide; the third instance
#     (R0 = 6803/66, d = 0.01, T = 103) disambiguates: R0 * 0.99 = 20409/200 = 102.045
#     (a terminating decimal, with the 99/66 cancellation, and a deliberate half-up tie at 2dp,
#     still below T = 103 so the stated assumption T > R1 holds tightly), whereas R0 * 0.01
#     = 6803/6600 would be a non-terminating, meaningless collapse to ~1.03.
#   * No compounding or time dimension: a single downturn followed by a single recovery step,
#     so the recovery rate is a simple ratio of the additional revenue needed to R1.
#   * Final answer in percent: 100 * (T - R1) / R1 (unrounded; framework rounds half-up to 2dp).
#   * The checkpoint is R1 in USD, unrounded (framework rounds half-up to 2dp, so 102.045 -> 102.05).
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h048"


def solve(text: str, q: dict) -> dict:
    r0 = grab(r"starts with revenue {N}", text)
    d = grab(r"downturn ratio {N}", text)
    target = grab(r"target revenue {N}", text)

    post = r0 * (1 - d)  # revenue immediately after the downturn
    # The text states the assumption target > post-downturn revenue; the formula
    # (target - post) / post is applied as worded (additional revenue / post-downturn revenue).
    rate_pct = (target - post) / post * 100

    return {"final": rate_pct, "slots": {"post_downturn_checkpoint": post}}
