"""h113 -- literal transcription solver (common-factor parametric loss vs stress loss).

Sentence-by-sentence transcription of the question:

S1  "A portfolio worth V has signed weighted common-factor return loadings l1 and l2,
     each expressed as a ratio."
        -> portfolio_value = V (usd); loadings = [l1, l2, ...] (signed ratios)

S2  "Under the stated common-factor covariance convention, aggregate the loadings before
     constructing the variance radicand."
        -> every loading sits on ONE common factor (unit-correlated covariance), so the
           signed loadings are aggregated (netted) FIRST:  aggregate = l1 + l2 + ...
           and only then is the variance radicand built:   radicand = aggregate ** 2
           portfolio volatility (ratio) = sqrt(radicand)  (= |aggregate|, computed exactly)

S3  "Apply confidence multiplier k, add liquidity charge L, and compare the result with
     stress loss S."
        -> parametric loss (usd) = k * sigma * V
           result (usd)          = parametric loss + L
           compared with stress loss S (usd)

S4  "Compute the required capital as the larger loss measure."
        -> required capital = max(result, S)

Slot portfolio_sigma_checkpoint = sigma (ratio, unrounded; framework rounds to 8 dp).
Final = required capital (usd, unrounded; framework rounds half-up to 2 dp).
"""

from __future__ import annotations

import math
import re
from fractions import Fraction

from finreason.nums import grab, numbers, sqrt as approx_sqrt

TEMPLATE_ID = "h113"


def _exact_sqrt(x: Fraction) -> Fraction:
    """Exact square root when x is a perfect square of a rational; else 80-digit fallback."""
    if x < 0:
        raise ValueError(f"negative variance radicand {x}")
    n, d = x.numerator, x.denominator  # Fraction is always in lowest terms
    rn, rd = math.isqrt(n), math.isqrt(d)
    if rn * rn == n and rd * rd == d:
        return Fraction(rn, rd)
    return approx_sqrt(x)


def solve(text: str, q: dict) -> dict:
    # --- S1: portfolio value and the signed common-factor return loadings (ratios)
    portfolio_value = grab(r"portfolio worth (?:USD\s*)?{N}", text)
    m = re.search(
        r"common-factor return loadings\s+(.*?),\s*each expressed as a ratio",
        text,
        flags=re.S,
    )
    if m is None:
        raise ValueError("loadings list not found")
    loadings = numbers(m.group(1))
    if len(loadings) < 2:
        raise ValueError(f"expected at least two loadings, got {loadings}")

    # --- S2: common-factor convention -> aggregate (net) the signed loadings first,
    #         then construct the variance radicand from the aggregate.
    aggregate_loading = sum(loadings, Fraction(0))
    variance_radicand = aggregate_loading ** 2
    portfolio_sigma = _exact_sqrt(variance_radicand)  # ratio

    # --- S3: confidence multiplier, liquidity charge, stress loss
    confidence_multiplier = grab(r"confidence multiplier {N}", text)
    liquidity_charge = grab(r"liquidity charge (?:of\s+)?(?:USD\s*)?{N}", text)
    stress_loss = grab(r"stress loss (?:of\s+)?(?:USD\s*)?{N}", text)

    parametric_loss = confidence_multiplier * portfolio_sigma * portfolio_value  # usd
    loss_with_liquidity = parametric_loss + liquidity_charge  # "the result"

    # --- S4: required capital = the larger loss measure
    required_capital = max(loss_with_liquidity, stress_loss)

    return {
        "final": required_capital,
        "slots": {"portfolio_sigma_checkpoint": portfolio_sigma},
    }
