"""h004 -- stress-test net reserve (market shock x sensitivity + liquidity shock, less recoveries).

FINANCE MODEL (standard conventions; no overrides in the text)
--------------------------------------------------------------
Inputs: V = portfolio value (USD), s = market shock ratio, b = loss sensitivity,
        l = liquidity shock ratio, rho = recovery ratio.

1. Market loss rate  = s * b          ("market shock ratio 0.2 with loss sensitivity b": the sensitivity
                                         converts a shock into a loss rate; sibling template defines the
                                         "market-shock loss ratio" the same way, = shock * sensitivity).
   Market stress dollar loss = V * s * b                      -> slot market_loss_checkpoint (USD).
2. Liquidity loss    = V * l          ("applied directly to portfolio value": no sensitivity factor).
3. Combined gross stress loss = market loss + liquidity loss.
4. Recoverable amount = rho * gross   ("recover ratio rho of the combined gross loss").
5. Net reserve required = gross - recoverable = gross * (1 - rho)   -> final answer (USD).
   Not floored/capped: text only says to subtract the recoverable amount from the gross loss.

All values exact Fractions; the framework rounds half up to 2 dp (final and checkpoint).
"""
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h004"


def solve(text: str, q: dict) -> dict:
    V = grab(r"portfolio worth {N}", text)
    shock = grab(r"market shock ratio {N}", text)
    sens = grab(r"loss sensitivity {N}", text)
    liq = grab(r"liquidity shock ratio {N}", text)
    rho = grab(r"recover ratio {N}", text)

    market_loss = V * shock * sens
    liquidity_loss = V * liq
    gross = market_loss + liquidity_loss
    recoverable = rho * gross
    net = gross - recoverable

    return {"final": net, "slots": {"market_loss_checkpoint": market_loss}}
