"""h031 -- stressed risk-appetite budget vs. excess-liquidity limit, with a liquidity gate.

FINANCE MODEL (written before coding)
-------------------------------------
Inputs: capital K; base risk-appetite ratio a0 (fraction of capital the firm is willing to put at risk);
downturn haircut h; volatility uplift u; liquid assets L; uncommitted reserve R; proposed exposure E.

1. Stressed appetite ratio (checkpoint, unit = plain ratio):
       a = a0 * (1 - h) / (1 + u)
   Convention: a "haircut" is a proportional cut (value * (1 - haircut)), so "reduce the base appetite by the
   downturn haircut" = multiply by (1 - h).  The volatility uplift is a proportional increase of the stress
   denominator, so "divide it by one plus the volatility uplift" = divide by (1 + u).
   (Supporting evidence for the multiplicative reading: base 0.500001 * 0.5 = 0.2500005, which sits exactly on a
   half-up boundary at 6 dp; base 0.5, capital 101 -> 25.25 vs excess liquidity 25 makes the liquidity cap bind.)
2. Stressed risk budget = a * K  (apply the stressed ratio to capital).
3. Available excess liquidity = max(L, R) - R   (floored at zero; a shortfall is NOT treated as covered).
4. Binding exposure limit = min(risk budget, available excess liquidity).
5. Decision:
       if L < R (original liquid assets do not cover reserve)  -> liquidity_block   (L == R covers the reserve)
       elif E <= binding limit ("within the binding limit", ties are within)       -> within_appetite
       else                                                                        -> reduce_exposure
Checkpoint "stressed_ratio_checkpoint" is the stressed appetite ratio a (before applying to capital), unrounded;
the framework rounds it to 6 dp half-up.  No overrides of standard conventions apart from those noted above.
"""
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h031"


def solve(text: str, q: dict) -> dict:
    capital = grab(r"capital\s+{N}", text)
    base = grab(r"base risk-appetite ratio\s+{N}", text)
    haircut = grab(r"downturn haircut\s+{N}", text)
    uplift = grab(r"volatility uplift\s+{N}", text)
    liquid = grab(r"liquid assets are\s+{N}", text)
    reserve = grab(r"of which\s+{N}\s+must remain uncommitted", text)
    exposure = grab(r"proposes exposure\s+{N}", text)

    stressed_ratio = base * (1 - haircut) / (1 + uplift)
    risk_budget = stressed_ratio * capital
    excess_liquidity = max(liquid, reserve) - reserve
    binding = min(risk_budget, excess_liquidity)

    if liquid < reserve:
        final = "liquidity_block"
    elif exposure <= binding:
        final = "within_appetite"
    else:
        final = "reduce_exposure"

    return {"final": final, "slots": {"stressed_ratio_checkpoint": stressed_ratio}}
