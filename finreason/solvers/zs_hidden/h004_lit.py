"""h004: portfolio stress loss (market + liquidity) net of recovery -> net reserve (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h004"


def solve(text: str, q: dict) -> dict:
    # "A portfolio worth {V}"
    value = grab(r"portfolio worth {N}", text)
    # "faces market shock ratio {m} with loss sensitivity {s}"
    market_shock = grab(r"market shock ratio {N}", text)
    sensitivity = grab(r"loss sensitivity {N}", text)
    # "plus liquidity shock ratio {l} applied directly to portfolio value"
    liquidity_shock = grab(r"liquidity shock ratio {N}", text)
    # "The institution expects to recover ratio {r} of the combined gross loss"
    recovery_ratio = grab(r"recover ratio {N}", text)

    # Market stress dollar loss = value * market shock * loss sensitivity
    market_loss = value * market_shock * sensitivity
    # Liquidity loss applied directly to portfolio value
    liquidity_loss = value * liquidity_shock
    # Combined gross stress loss
    gross_loss = market_loss + liquidity_loss
    # Recoverable amount
    recoverable = recovery_ratio * gross_loss
    # Net reserve = gross stress loss - recoverable amount
    net_reserve = gross_loss - recoverable

    return {
        "final": Fraction(net_reserve),
        "slots": {"market_loss_checkpoint": Fraction(market_loss)},
    }
