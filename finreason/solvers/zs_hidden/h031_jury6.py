"""h031 -- stressed risk-appetite limit vs. liquidity reserve (juror 6).

Reading of the text, sentence by sentence:

  * capital C, base appetite ratio r, downturn haircut h, volatility uplift u,
    liquid assets L, reserve R (must remain uncommitted), proposed exposure E.
  * "Reduce the base appetite by the downturn haircut" -> r - h  (subtractive:
    the uplift sentence is spelled out multiplicatively as "one plus", the
    haircut sentence is not, and the instances sit exactly on / just above the
    r == h boundary, which only matters under subtraction).
  * "divide it by one plus the volatility uplift" -> (r - h) / (1 + u) = stressed ratio (slot).
  * "apply the result to capital" -> stressed risk budget = C * stressed ratio (no floor stated).
  * available excess liquidity = max(L, R) - R  (floored at zero).
  * binding limit = min(stressed budget, available excess liquidity).
  * liquidity_block iff L < R ("do not cover" -> strictly less; L == R covers).
  * otherwise within_appetite iff E <= binding limit (non-strict "within"), else reduce_exposure.
"""

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h031"


def _num(pattern: str, text: str) -> Fraction:
    """Number captured by ``{N}`` in ``pattern``; a trailing '%' turns it into a ratio."""
    rx = pattern.replace("{N}", f"({NUMBER})") + r"\s*(%|percent)?"
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    val = F(m.group(1))
    return val / 100 if m.group(2) else val


def solve(text: str, q: dict) -> dict:
    capital = _num(r"capital\s+{N}", text)
    base = _num(r"risk-appetite ratio\s+{N}", text)
    haircut = _num(r"downturn haircut\s+(?:of\s+)?{N}", text)
    uplift = _num(r"volatility uplift\s+(?:of\s+)?{N}", text)
    liquid = _num(r"liquid assets are\s+{N}", text)
    reserve = _num(r"of which\s+{N}\s+must remain uncommitted", text)
    exposure = _num(r"proposes exposure\s+(?:of\s+)?{N}", text)

    # Both stress adjustments on the appetite ratio.
    stressed_ratio = (base - haircut) / (1 + uplift)
    stressed_budget = capital * stressed_ratio

    # Available excess liquidity, floored at zero (shortfall is NOT treated as covered).
    excess_liquidity = max(liquid, reserve) - reserve
    binding_limit = min(stressed_budget, excess_liquidity)

    if liquid < reserve:
        final = "liquidity_block"
    elif exposure <= binding_limit:
        final = "within_appetite"
    else:
        final = "reduce_exposure"

    return {"final": final, "slots": {"stressed_ratio_checkpoint": stressed_ratio}}
