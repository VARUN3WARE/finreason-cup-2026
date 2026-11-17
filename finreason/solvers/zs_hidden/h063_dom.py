# FINANCE MODEL (household budget cut, choose a response to close the funding gap)
#
#   B   = starting total budget
#   c   = cut rate (a fraction, 0.2 = 20%; applied multiplicatively to the budget)
#   P   = protected spending (must continue in full)
#   Fx  = planned flexible spending (intended to continue)
#   Lo  = minimum flexible spending (floor; flexible spending may not fall below it)
#   X   = maximum outside funding available
#
#   post_cut_budget = B * (1 - c)                      [checkpoint 1, USD]
#   intended spending = P + Fx
#   gap = max(0, intended spending - post_cut_budget)  (funding gap after the cut)
#   reducible = max(0, Fx - Lo)                        [checkpoint 2, USD]
#                  (flexible spending available for reduction, down to the floor)
#
#   Decision (each option is tested "alone" against the full gap, in priority order):
#     1. reduce_flexible_spending  if reducible >= gap   ("covers" -> at least the gap)
#     2. use_external_funding      elif X >= gap
#     3. no_feasible_response      otherwise
#
# Conventions / overrides: "covers the gap" is read as >= (an exactly equal amount covers it).
# The options are not combined (the text says "alone"). No rounding inside the computation.
from fractions import Fraction

from finreason.nums import grab, F

TEMPLATE_ID = "h063"


def solve(text: str, q: dict) -> dict:
    B = grab(r"total budget of {N}", text)
    c = grab(r"A cut of {N}", text)
    P = grab(r"protected spending of {N}", text)
    Fx = grab(r"planned flexible spending of {N}", text)
    Lo = grab(r"not fall below {N}", text)
    X = grab(r"at most {N} of outside funding", text)

    post_cut = B * (1 - c)
    gap = P + Fx - post_cut
    if gap < 0:
        gap = Fraction(0)
    reducible = Fx - Lo
    if reducible < 0:
        reducible = Fraction(0)

    if reducible >= gap:
        final = "reduce_flexible_spending"
    elif X >= gap:
        final = "use_external_funding"
    else:
        final = "no_feasible_response"

    return {
        "final": final,
        "slots": {
            "post_cut_budget_checkpoint": post_cut,
            "reducible_spending_checkpoint": reducible,
        },
    }
