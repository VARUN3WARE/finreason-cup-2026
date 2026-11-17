# ===========================================================================
# h113 -- FINANCE MODEL (written before the code)
# ===========================================================================
#
# Economic quantity
# -----------------
# Required capital for a portfolio that is exposed to ONE common return factor,
# set as the larger of (i) a volatility-scaled modelled loss with a liquidity
# add-on and (ii) an externally supplied stress loss.
#
# Inputs (all read from the text)
#   V    portfolio value, USD ("A portfolio worth V")
#   l_i  signed, already-weighted common-factor return loadings (plain ratios,
#        "each expressed as a ratio" -> NO percent conversion). Signs matter:
#        long and short exposures to the same factor offset each other.
#   z    confidence multiplier (plain number; a stipulated scale, not a quantile)
#   LC   liquidity charge, an absolute USD amount ("add liquidity charge")
#   S    stress loss, an absolute USD amount
#
# Step 1 -- common-factor covariance convention (perfect co-movement)
#   With a single common factor the covariance of positions i and j is the
#   product of their loadings, Cov_ij = l_i * l_j (diagonal included), so the
#   covariance matrix is rank one.  Portfolio variance is the sum over the whole
#   matrix, which equals the square of the summed loadings:
#       sum_i sum_j l_i l_j = (sum_i l_i)^2
#   The text says "aggregate the loadings before constructing the variance
#   radicand", i.e.
#       L        = sum_i l_i                 (signed sum, offsets allowed)
#       radicand = L^2                       (the portfolio variance)
#       sigma_p  = sqrt(radicand) = |L|      (nonnegative root; exact)
#   This is the same structure as the seen template
#   sigma_p = sqrt((w_A sigma_A + w_B sigma_B)^2) for rho = +1.
#   sigma_p is a plain ratio (checkpoint "portfolio_sigma_checkpoint", unit
#   ratio, rounded half-up to 8 dp by the framework; the exact value is used
#   downstream, never the rounded checkpoint).
#
# Step 2 -- modelled loss (USD)
#   Standard parametric loss: V * sigma_p * z, then the liquidity charge is an
#   additive USD add-on (the text order is "apply confidence multiplier, add
#   liquidity charge"):
#       modelled = V * sigma_p * z + LC
#   The multiplier scales the statistical volatility loss only; the liquidity
#   charge is an add-on and is NOT scaled by z and NOT scaled by V.
#
# Step 3 -- required capital
#   "compare the result with stress loss S ... required capital as the larger
#   loss measure":
#       capital = max(modelled, S)          (value only matters; ties identical)
#   The stress loss is compared as given (no liquidity charge added to it).
#
# Conventions / overrides noted
#   * Nothing in the text overrides the standard conventions above.
#   * No percent->ratio conversions anywhere: loadings are explicit ratios and
#     the multiplier, liquidity charge and stress loss are plain numbers.
#   * Final answer: round only the final capital half-up to 2 dp (framework).
#   * Everything is exact Fraction arithmetic; sigma_p is an exact rational
#     because the radicand is a perfect square by construction (abs(L)).
#
# Expected behaviour on the 3 instances (branch outcomes differ)
#   1: L = 0.00506499  -> modelled = 98*0.00506499 = 0.49636902 < S=3  -> 3.00
#   2: L = -0.4        -> modelled = 99*0.4        = 39.6       < S=81 -> 81.00
#   3: L = -0.02       -> modelled = 98*0.02*3+0.995 = 6.875    > S=3.05 -> 6.88
#      (6.875 is an exact half-up tie at 2 dp -> 6.88)
# ===========================================================================

import math
import re
from fractions import Fraction

from finreason.nums import F, after, before, grab, grab_all, numbers  # noqa: F401
from finreason.nums import sqrt as _hp_sqrt

TEMPLATE_ID = "h113"


def _nonneg_sqrt(x: Fraction) -> Fraction:
    """Nonnegative square root; exact when x is a perfect rational square."""
    if x < 0:
        raise ValueError("negative radicand")
    n, d = x.numerator, x.denominator
    rn, rd = math.isqrt(n), math.isqrt(d)
    if rn * rn == n and rd * rd == d:
        return Fraction(rn, rd)
    return _hp_sqrt(x)  # 80-digit fallback (not reached when radicand = L**2)


def _loadings(text: str) -> list[Fraction]:
    # Everything between "loadings" and ", each expressed as a ratio".
    m = re.search(r"common-factor return loadings\s+(.*?)\s*,\s*each expressed", text, re.S)
    if m is None:
        m = re.search(r"loadings\s+(.*?)\s*,\s*each expressed", text, re.S)
    if m is None:
        raise ValueError("loadings not found")
    vals = numbers(m.group(1))
    if not vals:
        raise ValueError("no loading values parsed")
    return vals


def solve(text: str, q: dict) -> dict:
    V = grab(r"portfolio worth {N}", text)
    loads = _loadings(text)
    z = grab(r"confidence multiplier {N}", text)
    LC = grab(r"liquidity charge {N}", text)
    S = grab(r"stress loss {N}", text)

    # Step 1: aggregate signed loadings first, then build the variance radicand.
    L = sum(loads, Fraction(0))
    radicand = L * L
    sigma = _nonneg_sqrt(radicand)  # == abs(L), exact

    # Step 2: modelled loss in USD = V * sigma * z + liquidity charge.
    modelled = V * sigma * z + LC

    # Step 3: required capital = larger loss measure.
    capital = modelled if modelled >= S else S

    return {
        "final": capital,
        "slots": {"portfolio_sigma_checkpoint": sigma},
    }
