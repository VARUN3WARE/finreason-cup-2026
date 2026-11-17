# FINANCE MODEL (h006): required factor shock for a partially exposed portfolio.
#
# Inputs:
#   V     = total portfolio value (USD)
#   s     = share of the portfolio exposed to the single factor (fraction, 0.5 = 50%)
#   beta  = signed sensitivity of the exposed portion to the factor (value change per unit
#           factor shock, as a proportion of exposed value; sign preserved)
#   dV*   = target portfolio value change (USD, signed)
#
# Linear first-order factor model (standard convention, no overrides in the text):
#   exposed value      E  = V * s                       (USD)   <- checkpoint 1
#   portfolio change   dV = E * beta * x                 (x = signed factor shock, decimal)
#   required shock     x  = dV* / (E * beta)             (decimal)
#   reported answer    100 * x                           (percent, signed, unrounded here)
#
# Notes / conventions:
#   - The unexposed portion (V - E) does not move.
#   - Sign of the shock is preserved (negative target with positive beta -> negative shock).
#   - "share 0.5" is a plain fraction (not percent), so it is used as-is.
#   - The checkpoint "factor-exposed portfolio value" is V * s (dollar value of the exposed
#     portion), not multiplied by beta.
#   - All arithmetic exact (Fraction); framework applies half-up rounding to 2 dp.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h006"


def solve(text: str, q: dict) -> dict:
    v = grab(r"portfolio is worth {N}", text)
    share = grab(r"only share {N} is exposed", text)
    beta = grab(r"signed sensitivity {N}", text)
    target = grab(r"target portfolio value change {N}", text)

    exposed = v * share
    shock = target / (exposed * beta)  # decimal factor shock
    return {
        "final": shock * 100,
        "slots": {"exposed_value_checkpoint": exposed},
    }
