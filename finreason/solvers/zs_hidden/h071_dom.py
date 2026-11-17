# FINANCE MODEL (h071)
#
# Quantity: maximum portfolio value V such that total loss exactly exhausts a combined loss budget.
#
#   market-shock loss      = V * (market shock ratio * loss sensitivity)
#                          -> "market-shock loss ratio" m = shock_ratio * loss_sensitivity  (per unit of V)
#                             (the shock ratio is the size of the shock; the loss sensitivity is the
#                              portfolio's exposure/beta to it, so the loss per unit value is the product)
#   liquidity-spread cost  = V * liquidity spread ratio  (s per unit of V)
#   "Both loss components scale with the same portfolio value" -> both are linear in the same V.
#
#   Constraint: V * (m + s) <= budget; "exactly exhausts" -> equality:
#       V = budget / (shock_ratio * loss_sensitivity + liquidity_spread_ratio)
#
# Checkpoint 1 (market_ratio_checkpoint) = m = shock_ratio * loss_sensitivity  (plain ratio, 6 dp half-up).
# Final answer = V in the same units as the budget (usd), 2 dp half-up (framework rounds).
# No overrides of standard conventions; budget is used as given (not divided by anything).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h071"


def solve(text: str, q: dict) -> dict:
    budget = grab(r"within {N}\.", text)
    shock = grab(r"market shock ratio is {N}", text)
    sens = grab(r"loss sensitivity is {N}", text)
    spread = grab(r"liquidity spread ratio is {N}", text)

    m = shock * sens                 # market-shock loss ratio (loss per unit of portfolio value)
    total = m + spread               # combined loss ratio
    value = budget / total           # portfolio value exhausting the budget

    slots = {}
    for s in q["trace_spec"]["slots"]:
        slots[s["slot_id"] if "slot_id" in s else s["id"]] = m
    return {"final": value, "slots": slots}
