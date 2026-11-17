from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h004"


def solve(text: str, q: dict) -> dict:
    value = grab(r"portfolio worth {N}", text)
    mkt_shock = grab(r"market shock ratio {N}", text)
    sens = grab(r"loss sensitivity {N}", text)
    liq_shock = grab(r"liquidity shock ratio {N}", text)
    recov = grab(r"recover ratio {N}", text)

    market_loss = value * mkt_shock * sens          # market stress dollar loss
    liquidity_loss = value * liq_shock              # applied directly to portfolio value
    gross = market_loss + liquidity_loss            # combined gross loss
    recoverable = recov * gross
    net = gross - recoverable

    return {"final": Fraction(net), "slots": {"market_loss_checkpoint": Fraction(market_loss)}}
