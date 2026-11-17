"""h067 -- premium threshold for a target simple expiration ROI on a cash-settled call (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h067"


def solve(text: str, q: dict) -> dict:
    # "A cash-settled call expires in the money at terminal stock price S with strike price K."
    terminal_price = grab(r"terminal stock price {N}", text)
    strike = grab(r"strike price {N}", text)

    # "Its intrinsic payoff is terminal price minus strike."
    intrinsic_payoff = terminal_price - strike

    # "Deduct the additional settlement fee F, which is separate from the strike ..."
    settlement_fee = grab(r"settlement fee {N}", text)

    # "For target ratio T, where 0.20 means 20%" -> T is a plain ratio.
    target = grab(r"target ratio {N}", text)

    # ROI = (intrinsic - fee - premium) / premium ; ROI = target
    # => intrinsic - fee = premium * (1 + target)
    # => premium threshold = (intrinsic - fee) / (1 + target)   (exact, unrounded)
    threshold = (intrinsic_payoff - settlement_fee) / (1 + target)

    # sanity: ROI at the threshold equals the target exactly
    assert threshold != 0
    assert (intrinsic_payoff - settlement_fee - threshold) / threshold == target

    return {
        "final": Fraction(threshold),
        "slots": {"intrinsic_checkpoint": Fraction(intrinsic_payoff)},
    }
