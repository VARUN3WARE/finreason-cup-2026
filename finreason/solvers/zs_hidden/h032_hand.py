"""h032: maximum management-fee rate subject to a Sharpe-ratio floor and a Jensen's-alpha floor.

net = gross - fee
Sharpe:  (net - rf) / sigma >= S          ->  fee <= gross - rf - S * sigma
Alpha:   net - [rf + beta (Rm - rf)] >= a  ->  fee <= gross - rf - beta * (Rm - rf) - a
Maximum fee = min of the two bounds (not floored at zero: a zero fee would violate a
binding constraint whose bound is negative, so the exact maximum is the min itself).
"""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h032"


def solve(text: str, q: dict) -> dict:
    gross = grab(r"gross expected return {N}", text)
    sigma = grab(r"volatility {N}", text)
    beta = grab(r"beta {N}", text)
    rm = grab(r"market return is {N}", text)
    rf = grab(r"risk-free rate is {N}", text)
    s_min = grab(r"Sharpe ratio of at least {N}", text)
    a_min = grab(r"alpha of at least {N}", text)

    mrp = rm - rf
    fee_sharpe = gross - rf - s_min * sigma
    fee_alpha = gross - rf - beta * mrp - a_min
    fee = min(fee_sharpe, fee_alpha)

    # sanity: both constraints hold at the exact maximum
    net = gross - fee
    assert (net - rf) / sigma >= s_min
    assert net - (rf + beta * mrp) >= a_min

    return {
        "final": Fraction(fee) * 100,
        "slots": {"market_premium_checkpoint": Fraction(mrp)},
    }
