# FINANCE MODEL (h005): carbon-credit vs internal-abatement breakeven price.
#
# Given:
#   K  = internal abatement capacity (tons CO2e)
#   u  = committed utilization (fraction of capacity actually planned for abatement)
#   F  = fixed mobilization cost of internal abatement (USD), incurred once
#   v  = variable cost per ton internally abated (USD/ton)
#
# Planned abatement quantity (checkpoint, tons CO2e):
#       Q = K * u          (utilization is a plain fraction, 0.5 = 50%)
#
# Internal abatement cost for the planned quantity:
#       C_int = F + v * Q
# Buying credits for the SAME planned quantity Q (1 credit = 1 ton CO2e):
#       C_credit = p * Q
# Breakeven (costs exactly equal):
#       p * Q = F + v * Q   =>   p = (F + v * Q) / Q = F / Q + v    (USD per ton CO2e)
#
# Conventions / notes:
#   - Credits needed = Q tons exactly (no rounding to whole credits: text does not ask for it).
#   - Fixed cost is incurred for the planned quantity only (Q > 0 assumed); no capacity-based cost.
#   - Return unrounded exact values; the framework rounds (final 2 dp, checkpoint 4 dp, half-up).

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h005"


def solve(text: str, q: dict) -> dict:
    cap = grab(r"internal abatement capacity {N} tons", text)
    util = grab(r"commits to utilization {N}", text)
    fixed = grab(r"Mobilizing internal abatement costs {N} USD", text)
    var = grab(r"plus {N} USD for each ton", text)

    planned = cap * util                    # tons CO2e
    price = fixed / planned + var           # USD per ton CO2e at breakeven

    return {"final": price, "slots": {"planned_abatement_checkpoint": planned}}
