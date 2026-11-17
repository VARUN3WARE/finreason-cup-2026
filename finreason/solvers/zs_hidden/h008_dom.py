# FINANCE MODEL (h008) -- implied residual value from a target carrying amount, straight-line depreciation
#
# Straight-line: annual (periodic) depreciation = (Cost - Residual) / Life.
# After a fraction f of the depreciable life has elapsed:
#     accumulated depreciation  AD = f * (Cost - Residual)
#     carrying amount           CA = Cost - AD = Cost - f * (Cost - Residual)
#
# Given: Cost C, elapsed fraction f (0.75 / 0.8 -- "of its depreciable life"), target carrying amount CA*.
# Unknown: residual value S such that CA(f) = CA*.
#
#   Step 1 (checkpoint, implied_depreciation_checkpoint, USD million):
#       AD = C - CA*                      (accumulated depreciation implied by cost and target carrying amount)
#   Step 2: depreciable base  D = C - S = AD / f
#   Step 3 (final, USD million):
#       S = C - AD / f  =  C - (C - CA*) / f
#
# Conventions / notes:
#   - Everything is in USD millions already; no unit conversion.
#   - No rounding inside the chain; framework rounds half-up to 2 dp at the end.
#   - "0.75 of its depreciable life has elapsed" is a plain fraction of life (not a percent).
#   - No floor at zero or other clamp is stated, so S is returned as computed (sign preserved).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h008"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"original cost {N} in USD millions", text)
    f = grab(r"{N} of its depreciable life has elapsed", text)
    target_ca = grab(r"target carrying amount of {N} at that point", text)

    acc_dep = cost - target_ca            # implied accumulated depreciation
    depreciable_base = acc_dep / f        # cost - residual
    residual = cost - depreciable_base

    return {"final": residual, "slots": {"implied_depreciation_checkpoint": acc_dep}}
