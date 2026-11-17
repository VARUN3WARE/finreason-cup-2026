"""h031 -- stressed risk-appetite vs liquidity limit (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h031"


def solve(text: str, q: dict) -> dict:
    # "A firm has capital C, base risk-appetite ratio R, a downturn haircut H, and a volatility uplift U."
    capital = grab(r"has capital {N}", text)
    base_ratio = grab(r"base risk-appetite ratio {N}", text)
    haircut = grab(r"downturn haircut {N}", text)
    uplift = grab(r"volatility uplift {N}", text)

    # "Its liquid assets are L, of which K must remain uncommitted, and it proposes exposure E."
    liquid_assets = grab(r"liquid assets are {N}", text)
    reserve = grab(r"of which {N} must remain uncommitted", text)
    proposed = grab(r"proposes exposure {N}", text)

    # "Reduce the base appetite by the downturn haircut, divide it by one plus the volatility
    #  uplift, and apply the result to capital."
    reduced = base_ratio * (1 - haircut)
    stressed_ratio = reduced / (1 + uplift)
    stressed_budget = stressed_ratio * capital

    # "Define available excess liquidity as max(liquid assets, the reserve) minus the reserve."
    excess_liquidity = max(liquid_assets, reserve) - reserve

    # "The binding exposure limit is the smaller of that stressed risk budget and available
    #  excess liquidity."
    binding = min(stressed_budget, excess_liquidity)

    # "Return liquidity_block if the original liquid assets do not cover the reserve, otherwise
    #  return within_appetite when proposed exposure is within the binding limit and
    #  reduce_exposure when it is not."
    if liquid_assets < reserve:
        final = "liquidity_block"
    elif proposed <= binding:
        final = "within_appetite"
    else:
        final = "reduce_exposure"

    return {"final": final, "slots": {"stressed_ratio_checkpoint": Fraction(stressed_ratio)}}
