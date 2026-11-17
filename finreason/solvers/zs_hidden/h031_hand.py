from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h031"


def solve(text: str, q: dict) -> dict:
    capital = grab(r"has capital {N}", text)
    base = grab(r"base risk-appetite ratio {N}", text)
    haircut = grab(r"downturn haircut {N}", text)
    uplift = grab(r"volatility uplift {N}", text)
    liquid = grab(r"liquid assets are {N}", text)
    reserve = grab(r"of which {N} must remain uncommitted", text)
    exposure = grab(r"proposes exposure {N}", text)

    # Reduce the base appetite by the downturn haircut (multiplicative haircut),
    # then divide by one plus the volatility uplift.
    stressed_ratio = base * (1 - haircut) / (1 + uplift)
    stressed_budget = stressed_ratio * capital

    available_excess = max(liquid, reserve) - reserve
    binding = min(stressed_budget, available_excess)

    if liquid < reserve:
        final = "liquidity_block"
    elif exposure <= binding:
        final = "within_appetite"
    else:
        final = "reduce_exposure"

    return {"final": final, "slots": {"stressed_ratio_checkpoint": Fraction(stressed_ratio)}}
