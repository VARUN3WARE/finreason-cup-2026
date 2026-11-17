# FINANCE MODEL (tax-loss harvesting vs. no-harvest, terminal wealth advantage)
#
# Given:
#   L   = eligible loss magnitude (USD), fully usable (no offset limits, no disallowance)
#   t   = current-year tax rate (decimal fraction, 0.5 = 50%; the text gives rates as plain decimals)
#   P   = original principal (USD)
#   r_i = intended exposure annual effective total return (decimal)
#   s   = additive annual tracking shortfall (decimal), subtracted from r_i
#   n   = number of whole years, annual compounding, dividends reinvested, no interim cash flows
#
# Model:
#   Immediate tax reduction (time 0)   T      = t * L           (loss magnitude times tax rate)
#   Tax-harvest path: invests P + T in the replacement exposure that earns r_rep = r_i - s
#        FV_harvest   = (P + T) * (1 + r_rep)^n
#   No-harvest path: original principal P stays in the intended exposure earning r_i, no tax cash
#        FV_noharvest = P * (1 + r_i)^n
#   Signed advantage (final answer, USD) = FV_harvest - FV_noharvest   (may be negative)
#
# Conventions / overrides: none beyond the text. Rates are decimals as printed (0.5 == 50%),
# not percents. Exponent n is an integer, so exact Fraction ** int is used. No rounding inside
# the computation; the framework rounds the final answer (2dp) and the checkpoint T (4dp).
# Checkpoint "immediate_tax_reduction_checkpoint" = T = t * L in USD (unrounded).

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h038"


def solve(text: str, q: dict) -> dict:
    loss = grab(r"eligible loss magnitude of {N} USD", text)
    tax_rate = grab(r"current-year tax rate is {N}", text)
    principal = grab(r"invests the original {N} USD principal", text)
    intended = grab(r"equal to the intended rate {N} minus", text)
    shortfall = grab(r"additive annual tracking shortfall {N}", text)
    years = grab(r"compound annually for {N} years", text)

    n = int(years)
    if Fraction(n) != years:
        raise ValueError("non-integer horizon")

    tax_reduction = tax_rate * loss
    r_rep = intended - shortfall

    fv_harvest = (principal + tax_reduction) * (1 + r_rep) ** n
    fv_no = principal * (1 + intended) ** n
    advantage = fv_harvest - fv_no

    return {
        "final": advantage,
        "slots": {"immediate_tax_reduction_checkpoint": tax_reduction},
    }
