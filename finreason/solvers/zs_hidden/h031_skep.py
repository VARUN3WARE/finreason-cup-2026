"""Hidden cluster h031 -- stressed risk appetite vs. excess liquidity (skeptic / ambiguity-hunting analyst).

Structure of the question
-------------------------
  capital C, base risk-appetite ratio a, downturn haircut h, volatility uplift u,
  liquid assets L, reserve R (must remain uncommitted), proposed exposure E.

  stressed_ratio = (a - h) / (1 + u)                     <- checkpoint "stressed_ratio_checkpoint" (unit: ratio)
  risk_budget    = stressed_ratio * C
  excess_liq     = max(L, R) - R                          (floored at zero by construction)
  limit          = min(risk_budget, excess_liq)
  final:
      L < R            -> "liquidity_block"   (liquid assets "do not cover" the reserve; checked FIRST)
      E <= limit       -> "within_appetite"
      otherwise        -> "reduce_exposure"

AMBIGUITIES CONSIDERED AND HOW EACH WAS RESOLVED (with textual evidence)
------------------------------------------------------------------------
A1. "Reduce the base appetite by the downturn haircut": subtract h, or multiply by (1 - h)?
    RESOLVED: SUBTRACT, a - h.
    - The author spells out the other adjustment multiplicatively and explicitly: "divide it by one plus the
      volatility uplift".  Had the haircut been multiplicative, the parallel wording "multiply by one minus the
      downturn haircut" would have been used; "reduce X by Y" with Y a like-unit ratio is plain subtraction.
    - Both the appetite and the haircut are given as bare ratios (0.5 / 0.5), i.e. like quantities.
    - The instances probe the boundary of a - h: base ratios {0.5, 0.500001, 2/3} against h = 0.5 give
      stressed ratios {0, 1e-6, 1/6}.  Such clustering of a around h only makes sense as a subtraction edge test.
A2. Order of the two stress adjustments: the text's order -- haircut first, then "divide IT by one plus the
    volatility uplift" ("it" = the already-reduced appetite).  Checkpoint = (a - h) / (1 + u).  With u = 0 the
    order is immaterial anyway.
A3. "apply the result to capital": multiply, risk_budget = stressed_ratio * C (a ratio applied to a base).
A4. Available excess liquidity: literally max(L, R) - R.  This is >= 0 always; a shortfall gives 0, never a
    negative number, and never "covers" anything (the shortfall is handled by the liquidity_block rule instead).
A5. "liquid assets do not cover the reserve": L < R (strict).  L == R covers the reserve (excess = 0) and the
    evaluation proceeds to the appetite test.
A6. "within the binding limit": inclusive, E <= limit -> within_appetite; E > limit -> reduce_exposure.
A7. Precedence: liquidity_block is tested first; "otherwise" the appetite comparison applies.
A8. The stressed ratio is NOT floored at zero -- the text floors only the liquidity leg.  If a < h the ratio is
    negative, the budget negative, the limit negative, and any non-negative exposure exceeds it (reduce_exposure).
    (Not exercised by the three instances, which all have a >= h.)
A9. Checkpoint content: "the appetite ratio after both stress adjustments" = (a - h)/(1 + u), a plain ratio,
    returned UNROUNDED; the framework rounds half-up to 6 dp.  The budget (ratio * capital) is NOT the checkpoint.
A10. Units: every input is a bare number (no "percent"/"%" wording).  A tolerant handler divides by 100 only if a
    percent marker directly follows the number; it never triggers on these instances.
A11. Rational inputs such as "2/3" are parsed exactly as Fractions (never floats).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h031"

_LINK = r"(?:\s+(?:of|is|at|equal\s+to|equals|=|:))?\s*(?:USD|usd|\$)?\s*"
_PCT = r"\s*(percent|%)?"


def _num(patterns: list[str], text: str) -> Fraction:
    """First matching pattern; `{N}` = number capture.  Divides by 100 only if a percent marker follows."""
    for pat in patterns:
        rx = pat.replace("{N}", f"({NUMBER})") + _PCT
        m = re.search(rx, text, flags=re.S | re.I)
        if m is not None:
            v = F(m.group(1))
            if m.group(2):
                v = v / 100
            return v
    raise ValueError(f"no match for any of {patterns!r}")


def solve(text: str, q: dict) -> dict:
    capital = _num([r"\bcapital" + _LINK + r"{N}"], text)
    base = _num([r"risk[- ]appetite ratio" + _LINK + r"{N}",
                 r"base appetite" + _LINK + r"{N}"], text)
    haircut = _num([r"downturn haircut" + _LINK + r"{N}",
                    r"\bhaircut" + _LINK + r"{N}"], text)
    uplift = _num([r"volatility uplift" + _LINK + r"{N}",
                   r"\buplift" + _LINK + r"{N}"], text)
    liquid = _num([r"liquid assets (?:are|is|of|total|amount to)?" + _LINK + r"{N}",
                   r"liquid assets" + _LINK + r"{N}"], text)
    reserve = _num([r"of which" + _LINK + r"{N}",
                    r"reserve" + _LINK + r"{N}"], text)
    exposure = _num([r"proposes (?:an? )?exposure" + _LINK + r"{N}",
                     r"proposed exposure" + _LINK + r"{N}",
                     r"\bexposure" + _LINK + r"{N}"], text)

    # A1/A2: subtract the haircut, then divide by (1 + uplift).  Unrounded ratio.
    stressed_ratio = (base - haircut) / (1 + uplift)
    # A3: apply the ratio to capital.
    risk_budget = stressed_ratio * capital
    # A4: excess liquidity floored at zero by the max() construction.
    excess_liq = max(liquid, reserve) - reserve
    # Binding limit = the smaller of the two.
    limit = min(risk_budget, excess_liq)

    # A5/A7: liquidity shortfall is tested first, on the ORIGINAL liquid assets.
    if liquid < reserve:
        final = "liquidity_block"
    # A6: inclusive "within".
    elif exposure <= limit:
        final = "within_appetite"
    else:
        final = "reduce_exposure"

    return {"final": final, "slots": {"stressed_ratio_checkpoint": stressed_ratio}}
