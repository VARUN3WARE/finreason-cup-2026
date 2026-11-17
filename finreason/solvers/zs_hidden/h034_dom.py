# MODEL
# A financial institution has a hard remediation budget B for ALL remediation.
# Aggregate remediation spending = capital_cost + liquidity_cost + exposure_charge, where
#     exposure_charge(E) = ratio * max(0, E - threshold)
# i.e. exposure up to the threshold is free, only the excess above the threshold is charged,
# at `ratio` per unit of excess (ratio is a plain multiplier, not a percent: "ratio 0.8").
# Fixed costs (capital + liquidity) are sunk and come first, so the budget left for the
# exposure charge is
#     charge_budget = B - capital - liquidity            (checkpoint 1; stated to be >= 0)
# Constraint: ratio * max(0, E - threshold) <= charge_budget
# The charge is nondecreasing in E, so the maximum feasible exposure is
#     E_max = threshold + charge_budget / ratio
# (if charge_budget == 0, E_max == threshold: excess above threshold would cost > 0).
# Spending exactly equal to the budget is allowed ("at most", "within budget").
# Units: all amounts are in USD (plain, as given); no unit scaling.
# Overrides of standard conventions: none.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h034"


def solve(text: str, q: dict) -> dict:
    budget = grab(r"can spend at most {N} on all remediation", text)
    capital = grab(r"Capital remediation already requires {N}", text)
    liquidity = grab(r"liquidity remediation requires {N}", text)
    threshold = grab(r"any exposure above {N} incurs", text)
    ratio = grab(r"charge at ratio {N} of the excess", text)

    charge_budget = budget - capital - liquidity
    if charge_budget < 0:
        # statement says budget exceeds fixed costs; guard anyway (no feasible charge room)
        charge_budget = Fraction(0)
    e_max = threshold + charge_budget / ratio
    return {"final": e_max, "slots": {"charge_budget_checkpoint": budget - capital - liquidity}}
