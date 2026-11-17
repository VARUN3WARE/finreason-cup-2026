"""h032: maximum management-fee rate subject to a Sharpe-ratio floor and a Jensen's-alpha floor.

Literal transcription of the question text, sentence by sentence.
"""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h032"


def solve(text: str, q: dict) -> dict:
    # S1: "a portfolio has gross expected return R, volatility s, and beta b."
    gross = grab(r"gross expected return {N}", text)
    vol = grab(r"volatility {N}", text)
    beta = grab(r"beta {N}", text)
    # S2: "The market return is Rm and the risk-free rate is rf."
    rm = grab(r"market return is {N}", text)
    rf = grab(r"risk-free rate is {N}", text)
    # S3: "net return equals gross return minus the fee; it does not change volatility,
    #      beta, the market return, or the risk-free rate."
    def net(fee: Fraction) -> Fraction:
        return gross - fee

    # S4: "Sharpe ratio of at least S and Jensen's alpha of at least A" (inclusive bounds).
    sharpe_min = grab(r"Sharpe ratio of at least {N}", text)
    alpha_min = grab(r"alpha of at least {N}", text)

    def sharpe(fee: Fraction) -> Fraction:
        return (net(fee) - rf) / vol

    market_premium = rm - rf  # used by the alpha (CAPM) constraint

    def jensen_alpha(fee: Fraction) -> Fraction:
        return net(fee) - (rf + beta * market_premium)

    # S5: maximum fee satisfying both constraints.
    # Sharpe: (gross - f - rf)/vol >= S  <=>  f <= gross - rf - S*vol   (vol > 0)
    fee_sharpe = gross - rf - sharpe_min * vol
    # Alpha: gross - f - (rf + beta*(Rm - rf)) >= A  <=>  f <= gross - rf - beta*(Rm-rf) - A
    fee_alpha = gross - rf - beta * market_premium - alpha_min
    fee_max = min(fee_sharpe, fee_alpha)

    # S6: test both constraints using the unrounded exact rate.
    assert vol > 0
    assert sharpe(fee_max) >= sharpe_min
    assert jensen_alpha(fee_max) >= alpha_min
    # maximality: any larger fee violates at least one constraint (linear bounds, one binds)
    assert sharpe(fee_max) == sharpe_min or jensen_alpha(fee_max) == alpha_min

    # Report as a percentage (framework rounds half up to 2 dp).
    return {
        "final": fee_max * 100,
        "slots": {"market_premium_checkpoint": market_premium},
    }
