from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h071"


def solve(text: str, q: dict) -> dict:
    budget = grab(r"liquidity-spread cost within {N}", text)
    shock = grab(r"market shock ratio is {N}", text)
    sens = grab(r"loss sensitivity is {N}", text)
    spread = grab(r"liquidity spread ratio is {N}", text)
    # Market-shock loss per unit of portfolio value = shock ratio x sensitivity.
    market_ratio = shock * sens
    # Liquidity-spread cost per unit of portfolio value = spread ratio.
    total_ratio = market_ratio + spread
    value = Fraction(budget) / total_ratio
    return {"final": value, "slots": {"market_ratio_checkpoint": market_ratio}}
