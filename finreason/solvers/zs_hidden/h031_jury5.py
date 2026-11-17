"""h031 -- stressed risk-appetite exposure limit with a liquidity reserve gate.

Reading of the text (juror 5):
  stressed_ratio   = (base_ratio - downturn_haircut) / (1 + volatility_uplift)
                     ("reduce the base appetite BY the haircut" = subtraction; the haircut is
                      given in the same ratio units as the base, and the instances probe
                      base == haircut and base == haircut + 1e-6, which only makes sense
                      under subtraction)
  risk_budget      = stressed_ratio * capital
  excess_liquidity = max(liquid, reserve) - reserve      (floored at zero, as stated)
  binding_limit    = min(risk_budget, excess_liquidity)
  decision:
      liquid < reserve          -> liquidity_block   (checked first, regardless of exposure)
      exposure <= binding_limit -> within_appetite   ("within" = non-strict)
      otherwise                 -> reduce_exposure
  slot stressed_ratio_checkpoint = stressed_ratio (plain ratio, unrounded)
"""

from fractions import Fraction

from finreason.nums import after

TEMPLATE_ID = "h031"


def solve(text: str, q: dict) -> dict:
    capital = after(text, "capital")
    base_ratio = after(text, "risk-appetite ratio")
    haircut = after(text, "downturn haircut")
    uplift = after(text, "volatility uplift")
    liquid = after(text, "liquid assets are")
    reserve = after(text, "of which")
    exposure = after(text, "proposes exposure")

    # Both stress adjustments applied to the appetite ratio.
    stressed_ratio = (base_ratio - haircut) / (Fraction(1) + uplift)
    risk_budget = stressed_ratio * capital

    # Available excess liquidity, floored at zero.
    excess_liquidity = max(liquid, reserve) - reserve

    binding_limit = min(risk_budget, excess_liquidity)

    if liquid < reserve:
        final = "liquidity_block"
    elif exposure <= binding_limit:
        final = "within_appetite"
    else:
        final = "reduce_exposure"

    return {"final": final, "slots": {"stressed_ratio_checkpoint": stressed_ratio}}
