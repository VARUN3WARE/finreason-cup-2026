"""h078: maximum exposure under a parametric VaR budget with square-root-of-time scaling.

VaR = exposure * z * sigma_daily * sqrt(horizon)  <=  budget
=> exposure_max = budget / (z * sigma_daily * sqrt(horizon))
Checkpoint: horizon volatility = sigma_daily * sqrt(horizon) (ratio).
"""
from fractions import Fraction
from math import isqrt

from finreason.nums import grab, sqrt

TEMPLATE_ID = "h078"


def _exact_sqrt(x: Fraction) -> Fraction:
    """Exact square root when x is a perfect rational square, else 80-digit sqrt."""
    if x >= 0:
        n, d = x.numerator, x.denominator
        rn, rd = isqrt(n), isqrt(d)
        if rn * rn == n and rd * rd == d:
            return Fraction(rn, rd)
    return sqrt(x)


def solve(text: str, q: dict) -> dict:
    budget = grab(r"VaR budget of (?:USD )?\$?{N}", text)
    sigma = grab(r"daily volatility (?:of )?{N}", text)
    z = grab(r"confidence multiplier (?:of )?{N}", text)
    horizon = grab(r"held for {N}", text)

    horizon_vol = sigma * _exact_sqrt(horizon)
    exposure = budget / (z * horizon_vol)
    return {"final": exposure, "slots": {"horizon_volatility_checkpoint": horizon_vol}}
