from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h031"


def solve(text: str, q: dict) -> dict:
    capital = grab(r"capital\s+{N}", text)
    base = grab(r"base risk-appetite ratio\s+{N}", text)
    haircut = grab(r"downturn haircut\s+{N}", text)
    uplift = grab(r"volatility uplift\s+{N}", text)
    liquid, reserve = grab_all(r"liquid assets are\s+{N}, of which\s+{N} must", text)
    exposure = grab(r"proposes exposure\s+{N}", text)

    # "Reduce the base appetite by the downturn haircut" -> plain subtraction in ratio units;
    # then "divide it by one plus the volatility uplift"; then "apply the result to capital".
    stressed_ratio = (base - haircut) / (1 + uplift)
    risk_budget = stressed_ratio * capital

    # available excess liquidity = max(liquid, reserve) - reserve (floored at 0)
    excess = max(liquid, reserve) - reserve
    limit = min(risk_budget, excess)

    if liquid < reserve:  # original liquid assets do not cover the reserve
        final = "liquidity_block"
    elif exposure <= limit:  # "within the binding limit" -> non-strict
        final = "within_appetite"
    else:
        final = "reduce_exposure"

    return {"final": final, "slots": {"stressed_ratio_checkpoint": stressed_ratio}}
