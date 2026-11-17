from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h031"


def solve(text: str, q: dict) -> dict:
    capital = grab(r"capital\s+{N}", text)
    base = grab(r"base risk-appetite ratio\s+{N}", text)
    haircut = grab(r"downturn haircut\s+{N}", text)
    uplift = grab(r"volatility uplift\s+{N}", text)
    liquid = grab(r"liquid assets are\s+{N}", text)
    reserve = grab(r"of which\s+{N}\s+must remain", text)
    exposure = grab(r"proposes exposure\s+{N}", text)

    # "Reduce the base appetite by the downturn haircut" -> proportional haircut (1 - h);
    # then "divide it by one plus the volatility uplift". No intermediate rounding.
    stressed_ratio = base * (1 - haircut) / (1 + uplift)
    risk_budget = stressed_ratio * capital

    # floors at zero; a shortfall is NOT treated as covered (handled by the block test below)
    excess_liquidity = max(liquid, reserve) - reserve
    binding = min(risk_budget, excess_liquidity)

    if liquid < reserve:
        final = "liquidity_block"
    elif exposure <= binding:
        final = "within_appetite"
    else:
        final = "reduce_exposure"

    return {"final": final, "slots": {"stressed_ratio_checkpoint": stressed_ratio}}
