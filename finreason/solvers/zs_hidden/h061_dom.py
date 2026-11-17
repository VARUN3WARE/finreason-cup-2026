# h061 -- revenue required for a target after-tax income (CVP / income-statement back-solve)
#
# FINANCE MODEL
#   Income statement as a function of revenue R (USD millions):
#       variable COGS          = v * R                (v = variable COGS rate, ratio of revenue)
#       gross profit           = (1 - v) * R
#       operating income EBIT  = (1 - v) * R - F      (F = fixed operating costs)
#       pre-tax income EBT     = EBIT - I             (I = interest expense)
#       net income NI          = EBT * (1 - t)        (t = income tax rate, ratio; flat tax on EBT)
#   Target: NI = N (after-tax income).
#   Back-solve:
#       retention ratio        = 1 - t                (after-tax retention ratio, slot 1)
#       required pre-tax income EBT* = N / (1 - t)
#       required R             = (EBT* + I + F) / (1 - v)
#   Conventions / overrides: none.  Rates are ratios (0.2 means 20%), not percents.  No tax-loss
#   or floor logic is stated, and the target after-tax income is positive in every instance,
#   so the plain flat-tax formula applies.  Final answer is in usd_million (inputs are already
#   in USD millions); retention ratio is a plain ratio.
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h061"


def solve(text: str, q: dict) -> dict:
    v = grab(r"variable COGS rate ratio of {N}", text)
    fixed = grab(r"fixed operating costs of {N}", text)
    interest = grab(r"interest expense of {N}", text)
    t = grab(r"income tax rate ratio of {N}", text)
    target = grab(r"after-tax income of {N}", text)

    retention = 1 - t
    pretax_needed = target / retention
    revenue = (pretax_needed + interest + fixed) / (1 - v)

    return {
        "final": revenue,
        "slots": {"retention_ratio_checkpoint": retention},
    }
