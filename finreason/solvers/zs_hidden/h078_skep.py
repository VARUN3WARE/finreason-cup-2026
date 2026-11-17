"""h078 -- maximum exposure under a parametric VaR budget with square-root-of-time scaling.

Structure (same in all 3 instances):
    "A risk desk permits a VaR budget of B. The position has daily volatility s, uses confidence
     multiplier z, and is held for T. Under square-root-of-time scaling, compute the maximum
     portfolio exposure that keeps parametric VaR within the budget."

Model:
    parametric VaR(E) = z * s * sqrt(T) * E            (no drift term is mentioned -> none applied)
    keep VaR within budget  <=>  z * s * sqrt(T) * E <= B
    maximum exposure        E_max = B / (z * s * sqrt(T))

Checkpoint (position 1) horizon_volatility_checkpoint, unit "ratio", 6 dp half-up:
    "Report volatility scaled to the holding horizon"  ->  s * sqrt(T)   (WITHOUT the multiplier z)

AMBIGUITIES CONSIDERED AND RESOLUTIONS
1. Unit of the holding period ("held for 9"): no unit word. The volatility is DAILY and the text
   says "square-root-of-time scaling", so T is taken as a number of daily periods and the scaling
   factor is sqrt(T) applied directly to the daily volatility. No day-count conversion (252/250)
   is applied because none is stated.
2. Does the checkpoint include the confidence multiplier?  The slot says "volatility scaled to
   the holding horizon": that is a volatility (s*sqrt(T)), not a VaR-per-unit (z*s*sqrt(T)).
   The multiplier is applied afterwards when forming VaR.  Resolution: checkpoint = s*sqrt(T).
3. Percent vs ratio: volatility is given as a bare decimal ("0.1"), the checkpoint unit is
   "ratio", so no /100.  For robustness, if the text ever says "percent"/"%" right after the
   volatility number, it is converted to a ratio.
4. "within the budget": VaR <= B (non-strict).  The maximum exposure is the boundary value
   B / (z*s*sqrt(T)); no rounding down / whole-unit truncation because none is stated.
5. Confidence multiplier is given directly as a z-multiplier (3), not as a confidence level.
   It is used as-is.
6. Budget is in the answer currency (usd); exposure is budget divided by VaR-per-unit-exposure,
   so it is also in usd.  No unit conversion.
7. sqrt(T): computed exactly when T is a perfect-square rational (all 3 instances: 9, 4, 9);
   otherwise the 80-digit high-precision sqrt helper is used.  All intermediate values are
   returned unrounded; the framework applies the spec rounding.
8. No drift / expected-return adjustment, no diversification or correlation adjustment: the text
   mentions none.
"""

from __future__ import annotations

import math
import re
from fractions import Fraction

from finreason.nums import F, NUMBER, grab, sqrt as hp_sqrt

TEMPLATE_ID = "h078"


def _exact_sqrt(x: Fraction) -> Fraction:
    """Exact square root when x is a perfect-square rational, else 80-digit precision."""
    x = Fraction(x)
    if x < 0:
        raise ValueError("negative value under square root")
    n, d = x.numerator, x.denominator
    rn, rd = math.isqrt(n), math.isqrt(d)
    if rn * rn == n and rd * rd == d:
        return Fraction(rn, rd)
    return hp_sqrt(x)


def _grab_first(patterns: list[str], text: str) -> Fraction:
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError:
            continue
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def _is_percent_after(pattern: str, text: str) -> bool:
    """True if the number captured by ``pattern`` is immediately followed by a percent marker."""
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        return False
    tail = text[m.end(1): m.end(1) + 12]
    return bool(re.match(r"\s*(%|percent|per cent)", tail, flags=re.I))


def solve(text: str, q: dict) -> dict:
    # --- VaR budget B (currency amount)
    budget_patterns = [
        r"VaR budget of (?:USD\s*|\$\s*)?{N}",
        r"budget of (?:USD\s*|\$\s*)?{N}",
        r"VaR budget (?:is|of|equal to)?\s*(?:USD\s*|\$\s*)?{N}",
        r"budget (?:is|of)?\s*(?:USD\s*|\$\s*)?{N}",
    ]
    B = _grab_first(budget_patterns, text)

    # --- daily volatility s (ratio)
    vol_patterns = [
        r"daily volatility (?:of|is|equal to)?\s*{N}",
        r"volatility (?:of|is|equal to)?\s*{N}",
        r"daily (?:standard deviation|sigma) (?:of|is)?\s*{N}",
    ]
    s = _grab_first(vol_patterns, text)
    for p in vol_patterns:
        try:
            grab(p, text)
        except ValueError:
            continue
        if _is_percent_after(p, text):
            s = s / 100
        break

    # --- confidence multiplier z
    z_patterns = [
        r"confidence multiplier (?:of|is|equal to)?\s*{N}",
        r"multiplier (?:of|is|equal to)?\s*{N}",
        r"z[- ]?(?:score|multiplier|factor) (?:of|is)?\s*{N}",
    ]
    z = _grab_first(z_patterns, text)

    # --- holding horizon T (number of daily periods)
    T_patterns = [
        r"held for {N}",
        r"holding (?:period|horizon) (?:of|is|equal to)?\s*{N}",
        r"horizon (?:of|is|equal to)?\s*{N}",
        r"held over {N}",
        r"for {N} (?:trading )?days?",
    ]
    T = _grab_first(T_patterns, text)

    # --- computation
    horizon_vol = s * _exact_sqrt(T)         # volatility scaled to the holding horizon
    var_per_unit = z * horizon_vol           # VaR per 1 unit of exposure
    if var_per_unit == 0:
        raise ValueError("VaR per unit of exposure is zero; exposure unbounded")
    max_exposure = B / var_per_unit          # VaR(E) <= B  ->  E_max = B / (z s sqrt(T))

    return {
        "final": max_exposure,
        "slots": {"horizon_volatility_checkpoint": horizon_vol},
    }
