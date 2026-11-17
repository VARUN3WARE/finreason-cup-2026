# FINANCE MODEL (h055): stress loss of a portfolio under a downside shock with a
# second-order (convexity) term, capped and compared with a loss budget.
#
# Inputs
#   V  = portfolio value ("A portfolio worth V")                       [dollars]
#   s  = positive downside shock ratio                                 [ratio of value]
#   d  = linear loss sensitivity                                       [loss rate per unit shock]
#   c  = convexity multiplier, applied to the SQUARE of the shock      [dimensionless]
#   K  = cap on the gross dollar loss ("cap that loss at K")           [dollars]
#   B  = loss budget                                                   [dollars]
#
# Model
#   linear loss rate     = d * s            (sensitivity times shock)
#   convexity loss rate  = c * s^2          (multiplier applied to shock squared; no 1/2 factor,
#                                            since the text says the multiplier applies to the square)
#   total loss rate      = d*s + c*s^2      ("Add the linear and convexity loss rates")
#   gross dollar loss    = V * total rate   ("convert the result to a gross dollar loss")
#   capped loss          = min(gross, K)    ("cap that loss at K")
#   verdict              = within_budget if capped <= B (does NOT exceed -> ties are within_budget)
#                          else budget_breach
#
# Checkpoint: "convexity loss ratio" = the convexity loss rate c * s^2 as a plain ratio
#   (the quantity of the stated chain's second term, before adding / converting to dollars).
#
# Overrides of standard conventions: none. All arithmetic exact (Fraction).

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h055"


def solve(text: str, q: dict) -> dict:
    V = grab(r"portfolio worth {N}", text)
    s = grab(r"downside shock ratio {N}", text)
    d = grab(r"linear loss sensitivity is {N}", text)
    c = grab(r"convexity multiplier {N}", text)
    K = grab(r"cap that loss at {N}", text)
    B = grab(r"budget {N}", text)

    linear_rate = d * s
    convexity_rate = c * s ** 2
    total_rate = linear_rate + convexity_rate
    gross = V * total_rate
    capped = gross if gross <= K else K

    final = "within_budget" if capped <= B else "budget_breach"
    return {"final": final, "slots": {"convexity_ratio_checkpoint": convexity_rate}}
