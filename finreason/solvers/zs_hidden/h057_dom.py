# FINANCE MODEL (h057): unit gross-profit retention after a price discount and unit-cost change.
#
# Given:
#   P  = original (undiscounted) unit price, USD
#   m  = baseline gross margin ratio, defined on the SAME undiscounted price P:  m = (P - C0) / P
#   d  = discount rate, applied as a fraction of the ORIGINAL price (discount amount = d * P)
#   C1 = post-change unit cost, USD (given directly; the baseline cost C0 is not needed)
#
# Baseline unit cost:           C0 = P * (1 - m)            (not used further)
# Baseline unit gross profit:   GP0 = P - C0 = P * m
# Discounted unit price:        Pd = P * (1 - d)            <-- checkpoint 1 (USD, before subtracting cost)
# Post-change unit gross profit: GP1 = Pd - C1              (may be negative or exceed GP0)
# Retention (percent):          R = GP1 / GP0 * 100         <-- final answer (percent, NOT a margin on Pd)
#
# Conventions / overrides noted:
#   - The final is a gross-profit RETENTION percentage (GP1 / GP0), not GP1 / Pd.
#   - Checkpoint is computed independently from the original inputs and is NOT fed downstream
#     (though mathematically Pd is the same exact value used in GP1).
#   - Everything exact Fraction; no intermediate rounding; framework rounds final to 2 dp half-up,
#     checkpoint to 4 dp half-up.
#   - Unit: "percent" -> value is multiplied by 100.

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h057"


def solve(text: str, q: dict) -> dict:
    price = grab(r"original unit price is {N} USD", text)
    margin = grab(r"baseline gross margin ratio is {N}", text)
    disc = grab(r"discounted by {N} of the original price", text)
    new_cost = grab(r"post-change unit cost is {N} USD", text)

    base_gp = price * margin                 # P - P(1-m) = P*m
    disc_price = price * (1 - disc)          # discounted unit price
    new_gp = disc_price - new_cost           # post-change unit gross profit
    retention_pct = new_gp / base_gp * 100

    return {
        "final": retention_pct,
        "slots": {"discounted_unit_price_checkpoint": disc_price},
    }
