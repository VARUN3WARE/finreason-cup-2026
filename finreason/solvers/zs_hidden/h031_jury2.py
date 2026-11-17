from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h031"


def solve(text: str, q: dict) -> dict:
    capital = grab(r"capital {N}", text)
    base = grab(r"base risk-appetite ratio {N}", text)
    haircut = grab(r"downturn haircut {N}", text)
    uplift = grab(r"volatility uplift {N}", text)
    liquid = grab(r"liquid assets are {N}", text)
    reserve = grab(r"of which {N} must remain uncommitted", text)
    exposure = grab(r"proposes exposure {N}", text)

    # Haircut is a proportional reduction of the base appetite ratio.
    stressed = base * (1 - haircut) / (1 + uplift)
    budget = stressed * capital
    excess = max(liquid, reserve) - reserve
    binding = min(budget, excess)

    if liquid < reserve:
        final = "liquidity_block"
    elif exposure <= binding:
        final = "within_appetite"
    else:
        final = "reduce_exposure"

    return {"final": final, "slots": {"stressed_ratio_checkpoint": stressed}}
