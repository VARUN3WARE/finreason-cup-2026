"""h078 -- maximum exposure under a parametric VaR budget with square-root-of-time scaling.

Literal transcription:
  "permits a VaR budget of B"                 -> budget
  "daily volatility s"                        -> sigma_daily
  "confidence multiplier z"                   -> z
  "held for T"                                -> horizon (days)
  "square-root-of-time scaling"               -> sigma_h = sigma_daily * sqrt(T)
  parametric VaR = exposure * z * sigma_h <= budget
  -> max exposure = budget / (z * sigma_h)
"""
from fractions import Fraction
from math import isqrt

from finreason.nums import grab, sqrt as real_sqrt

TEMPLATE_ID = "h078"


def _sqrt(x: Fraction) -> Fraction:
    """Exact square root when x is a perfect rational square, else 80-digit root."""
    x = Fraction(x)
    n, d = x.numerator, x.denominator
    rn, rd = isqrt(n), isqrt(d)
    if rn * rn == n and rd * rd == d:
        return Fraction(rn, rd)
    return real_sqrt(x)


def solve(text: str, q: dict) -> dict:
    # "A risk desk permits a VaR budget of B."
    budget = grab(r"VaR budget of {N}", text)
    # "The position has daily volatility s,"
    sigma_daily = grab(r"daily volatility {N}", text)
    # "uses confidence multiplier z,"
    z = grab(r"confidence multiplier {N}", text)
    # "and is held for T."
    horizon = grab(r"held for {N}", text)

    # "Under square-root-of-time scaling" -> horizon volatility
    sigma_h = sigma_daily * _sqrt(horizon)

    # parametric VaR = exposure * z * sigma_h ; keep within budget -> max exposure
    exposure = budget / (z * sigma_h)

    return {
        "final": exposure,
        "slots": {"horizon_volatility_checkpoint": sigma_h},
    }
