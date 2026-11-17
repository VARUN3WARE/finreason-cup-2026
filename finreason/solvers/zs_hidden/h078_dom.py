# FINANCE MODEL (h078) -- maximum exposure under a parametric (variance-covariance) VaR budget
#
# Standard parametric VaR with square-root-of-time scaling:
#     horizon_vol = daily_vol * sqrt(T)                 (ratio, fraction of position value)
#     VaR         = z * horizon_vol * Exposure           (z = "confidence multiplier", given directly; no
#                                                         inverse-normal lookup, no drift/mean term)
# VaR must stay within the budget:  VaR <= budget
#     =>  Exposure_max = budget / (z * daily_vol * sqrt(T))      (USD, binding constraint VaR == budget)
#
# Inputs and where they enter:
#   budget  = "VaR budget of {N}"            -> numerator (USD, same unit as the answer)
#   sigma_d = "daily volatility {N}"         -> ratio per day
#   z       = "confidence multiplier {N}"    -> multiplies horizon volatility
#   T       = "held for {N}"                 -> holding period in days (square-root-of-time scaling)
#
# Checkpoint horizon_volatility_checkpoint = "volatility scaled to the holding horizon" = sigma_d * sqrt(T)
#   (a ratio; the confidence multiplier is NOT included because the multiplier is a separate quantity --
#    including it would be the "VaR percentage", not the horizon volatility).
#
# Overrides of standard conventions: none. Square roots are taken exactly when T is a perfect square
# (rational square), otherwise via 80-digit finreason.nums.sqrt.

from fractions import Fraction
from math import isqrt

from finreason.nums import grab, sqrt as _sqrt_hp

TEMPLATE_ID = "h078"


def _exact_sqrt(x: Fraction) -> Fraction:
    """Exact sqrt if x is a rational square, else 80-digit approximation."""
    x = Fraction(x)
    if x < 0:
        raise ValueError("negative sqrt")
    n, d = x.numerator, x.denominator
    rn, rd = isqrt(n), isqrt(d)
    if rn * rn == n and rd * rd == d:
        return Fraction(rn, rd)
    return _sqrt_hp(x)


def solve(text: str, q: dict) -> dict:
    budget = grab(r"VaR budget of {N}", text)
    sigma = grab(r"daily volatility {N}", text)
    z = grab(r"confidence multiplier {N}", text)
    T = grab(r"held for {N}", text)

    horizon_vol = sigma * _exact_sqrt(T)          # ratio
    var_per_usd = z * horizon_vol                 # VaR per USD of exposure
    exposure = budget / var_per_usd               # max exposure keeping VaR <= budget

    return {
        "final": exposure,
        "slots": {"horizon_volatility_checkpoint": horizon_vol},
    }
