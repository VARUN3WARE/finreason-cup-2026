"""Hidden cluster h113: common-factor VaR with liquidity add-on vs stress loss.

Structure (from the text alone):
  * portfolio value V (USD);
  * signed weighted common-factor return loadings L_i (ratios);
  * common-factor covariance convention: aggregate the signed loadings first,
    A = sum(L_i), then build the variance radicand A**2 (all exposures load on
    the one common factor, so cross terms are L_i*L_j and the variance is
    (sum L_i)**2); portfolio volatility sigma = sqrt(A**2) = |A| (exact);
  * parametric loss = confidence multiplier * sigma * V, plus the liquidity
    charge (USD);
  * required capital = the larger of that loss measure and the stress loss.

Checkpoint: portfolio volatility sigma (ratio), unrounded (framework rounds
half-up to 8 places).  Final: required capital in USD, unrounded.
"""

from fractions import Fraction
import re

from finreason.nums import grab, numbers

TEMPLATE_ID = "h113"


def _loadings(text: str) -> list[Fraction]:
    # Every signed loading listed between "loadings" and "each expressed as a ratio".
    m = re.search(r"loadings\s+(.*?)(?:,?\s*each expressed|\.\s)", text, flags=re.S)
    if m is None:
        raise ValueError("loadings not found")
    vals = numbers(m.group(1))
    if not vals:
        raise ValueError("no loading values parsed")
    return vals


def solve(text: str, q: dict) -> dict:
    value = grab(r"portfolio worth (?:USD )?{N}", text)
    loads = _loadings(text)
    z = grab(r"confidence multiplier (?:of )?{N}", text)
    liquidity = grab(r"liquidity charge (?:of )?(?:USD )?{N}", text)
    stress = grab(r"stress loss (?:of )?(?:USD )?{N}", text)

    aggregate = sum(loads, Fraction(0))        # signed aggregation before the radicand
    radicand = aggregate * aggregate           # variance under the common-factor convention
    sigma = abs(aggregate)                     # exact square root of a perfect square
    assert sigma * sigma == radicand and sigma >= 0

    parametric = z * sigma * value             # confidence multiplier x volatility x value
    loss_measure = parametric + liquidity      # add liquidity charge (USD)
    capital = max(loss_measure, stress)        # larger loss measure

    return {"final": capital, "slots": {"portfolio_sigma_checkpoint": sigma}}
