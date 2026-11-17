"""h113 -- single-common-factor VaR-style capital with liquidity charge and stress-loss floor.

Structure (all three instances):
    "A portfolio worth V has signed weighted common-factor return loadings b1 and b2, each expressed
     as a ratio. Under the stated common-factor covariance convention, aggregate the loadings before
     constructing the variance radicand. Apply confidence multiplier k, add liquidity charge c, and
     compare the result with stress loss S. Compute the required capital as the larger loss measure."
    Checkpoint portfolio_sigma_checkpoint (unit ratio, 8 dp half-up): portfolio volatility.
    Final (unit usd, 2 dp half-up): required capital.

AMBIGUITY HUNT -- points where two analysts could disagree, and the textual resolution:

A1. How are the loadings aggregated?  Candidates: signed sum (netting), sum of absolute values,
    root-sum-of-squares (independent factors).
    Resolution: signed sum.  The loadings are explicitly "signed"; the "common-factor covariance
    convention" means both exposures are to ONE common factor (perfectly correlated), so the
    portfolio variance is (sum of signed loadings)^2 -- the text says exactly that: "aggregate the
    loadings before constructing the variance radicand".  Hence L = b1 + b2 (with signs),
    radicand = L^2, sigma = sqrt(L^2) = |L|.  No factor volatility is supplied anywhere, so the
    loadings are already in return-volatility units ("return loadings ... expressed as a ratio").

A2. sqrt of the radicand.  sqrt(L^2) is exactly |L| (a rational); use abs() rather than the
    80-digit Decimal sqrt so the checkpoint stays exact (a 0-sum instance would otherwise be fine
    too, but abs is the exact value).  Volatility is non-negative by definition (positive root).

A3. What the checkpoint denotes.  "portfolio volatility" with unit "ratio" -> sigma = |L| as a
    plain ratio, NOT sigma*V (that would be usd) and NOT k*sigma (that is the VaR ratio).
    Returned unrounded; the framework rounds half-up to 8 dp.  The rounded checkpoint is never fed
    downstream (answer format: "use exact arithmetic through all intermediate steps").

A4. What the confidence multiplier applies to.  VaR-style: k multiplies the volatility (not the
    variance): loss ratio = k * sigma.

A5. Conversion to USD.  The final unit is usd and the stress loss is a USD amount (instance 2 has
    stress loss 81 on a portfolio worth 99 -- impossible as a ratio), so the loss measure compared
    with it must be in USD: result = k * sigma * V (+ charge).

A6. Liquidity charge unit and position.  It is "added" after the multiplier is applied and before
    the comparison, so it is a flat USD add-on: result = k*sigma*V + c.  Reading c as a ratio of V
    (0.995 of a 98 portfolio = 97.51) or as a ratio added to k*sigma before scaling would dwarf the
    VaR term and make no financial sense; as USD it is ~1% of the portfolio, a normal liquidity
    add-on.  Instances 1-2 have c = 0 so only instance 3 is sensitive to this.

A7. Comparison / tie rule.  "compare the result with stress loss S ... required capital as the
    larger loss measure" -> capital = max(result, S).  A tie gives the same value either way, so no
    tie-break matters.  Neither side can be negative (sigma >= 0, k, V, c, S >= 0), so no floor.

A8. Rounding.  Only the final is rounded (half-up, 2 dp) and only by the framework.  Instance 3
    lands exactly on a half (3*0.02*98 + 0.995 = 6.875 -> 6.88); exact Fractions make that certain.

A9. Convention branch.  All three instances state the common-factor (aggregate-first) convention.
    A defensive fallback (root-sum-of-squares) exists only for a hypothetical "independent factors"
    wording; it is not exercised by this cluster.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, numbers, sqrt

TEMPLATE_ID = "h113"


def _loadings(text: str) -> list[Fraction]:
    """All signed loadings listed between 'loadings' and 'each expressed'."""
    m = re.search(r"return loadings\s+(.*?),?\s+each expressed", text, flags=re.S)
    if m is None:
        raise ValueError("loadings segment not found")
    vals = numbers(m.group(1))
    if not vals:
        raise ValueError("no loadings parsed")
    return vals


def solve(text: str, q: dict) -> dict:
    value = grab(r"portfolio worth\s+{N}", text)                 # V, USD
    loads = _loadings(text)                                       # b_i, ratios (signed)
    k = grab(r"confidence multiplier\s+{N}", text)                # dimensionless
    charge = grab(r"liquidity charge\s+{N}", text)                # USD flat add-on (A6)
    stress = grab(r"stress loss\s+{N}", text)                     # USD

    # A1/A2: common-factor convention -> aggregate signed loadings first, then square, then root.
    if re.search(r"aggregate the loadings before", text):
        aggregate = sum(loads, Fraction(0))
        radicand = aggregate * aggregate
        sigma = abs(aggregate)                                    # exact sqrt(radicand)
    else:  # A9 defensive fallback: independent factors -> root-sum-of-squares
        radicand = sum((b * b for b in loads), Fraction(0))
        sigma = sqrt(radicand)

    # A4/A5/A6: VaR-style loss in USD, plus flat liquidity charge.
    result = k * sigma * value + charge

    # A7: required capital is the larger loss measure.
    capital = max(result, stress)

    return {"final": capital, "slots": {"portfolio_sigma_checkpoint": sigma}}
