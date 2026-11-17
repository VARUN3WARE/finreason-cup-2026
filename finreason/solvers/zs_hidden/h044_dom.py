# FINANCE MODEL (h044): early vs deferred cleanup, NPV difference.
#
# Given:
#   C   = valuation-date base cleanup estimate (real/base-date currency amount)
#   g   = nominal effective annual escalation rate (decimal ratio, annual compounding)
#   r   = nominal effective annual discount rate (decimal ratio, annual compounding)
#   Te  = year-end payment date of the early plan
#   Td  = year-end payment date of the deferred plan (terminal date)
#   A   = fixed NOMINAL administration outflow, paid only at Td (NOT escalated: it is
#         already stated as a nominal amount at the terminal date; it is only discounted)
#
# Cleanup cost paid at time T (nominal) = C * (1+g)^T   (annual compounding from valuation date t=0).
# Discount factor to date T            = 1 / (1+r)^T    (annual compounding; < 1).
# All outflows are costs, so NPV is negative of PV of costs; non-cleanup flows cancel.
#
#   PV_early    = C (1+g)^Te / (1+r)^Te
#   PV_deferred = (C (1+g)^Td + A) / (1+r)^Td
#   NPV(deferred) - NPV(early) = -PV_deferred - (-PV_early) = PV_early - PV_deferred
#   (positive => deferral favored, negative => early favored).
#
# Checkpoints:
#   1. early_cleanup_growth_factor_checkpoint = (1+g)^Te      (cumulative escalation factor, multiple)
#   2. terminal_discount_factor_checkpoint    = 1/(1+r)^Td    (cumulative discount factor, multiple)
#
# Overrides: none. Rates already decimal ratios (0.1 = 10%). If Te == Td the cleanup terms cancel and
# the result is simply -A/(1+r)^Td.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h044"


def solve(text: str, q: dict) -> dict:
    C = grab(r"base cleanup estimate is {N}", text)
    g = grab(r"escalation rate {N}", text)
    r = grab(r"nominal effective annual rate {N}", text)
    Te = grab(r"early plan pays the resulting cleanup cost at the end of year {N}", text)
    Td = grab(r"deferred plan pays the resulting cleanup cost at the end of year {N}", text)
    A = grab(r"administration outflow of {N}", text)

    if Te.denominator != 1 or Td.denominator != 1:
        raise ValueError("non-integer payment year")
    Te = int(Te)
    Td = int(Td)

    growth_early = (1 + g) ** Te
    growth_def = (1 + g) ** Td
    disc_early = 1 / ((1 + r) ** Te)
    disc_def = 1 / ((1 + r) ** Td)

    pv_early = C * growth_early * disc_early
    pv_def = (C * growth_def + A) * disc_def

    diff = pv_early - pv_def  # NPV(deferred) - NPV(early)

    return {
        "final": diff,
        "slots": {
            "early_cleanup_growth_factor_checkpoint": growth_early,
            "terminal_discount_factor_checkpoint": disc_def,
        },
    }
