"""h014 -- scenario-defined mean-variance score: solve for the total portfolio return.

Literal transcription of the question, sentence by sentence.
"""
from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h014"


def solve(text: str, q: dict) -> dict:
    # "Asset A has portfolio weight {wA} and Asset B receives the complementary weight."
    w_a = grab(r"Asset A has portfolio weight {N}", text)
    w_b = 1 - w_a

    # "Their return volatilities are {sA} and {sB}."
    vol_a, vol_b = grab_all(r"return volatilities are {N} and {N}", text)

    # "A risk engine supplies base weighted covariance cross-term contribution {base}
    #  and stress contribution {stress}; each already equals twice the product of both
    #  portfolio weights and the regime covariance."  -> used as-is (no further scaling).
    base_contrib = grab(r"base weighted covariance cross-term contribution {N}", text)
    stress_contrib = grab(r"and stress contribution {N}", text)

    # "Use the stress contribution when {x} is at least {y}, and otherwise use the base contribution."
    cond_x, cond_y = grab_all(r"Use the stress contribution when {N} is at least {N}", text)
    selected = stress_contrib if cond_x >= cond_y else base_contrib

    # "Portfolio variance is the sum of the two squared weight-scaled volatilities and the
    #  selected contribution."
    weighted_vol_a = w_a * vol_a
    weighted_vol_b = w_b * vol_b
    variance = weighted_vol_a ** 2 + weighted_vol_b ** 2 + selected

    # "The score equals portfolio excess return minus {lam} times variance."
    lam = grab(r"minus {N} times variance", text)

    # "What total portfolio return makes this score equal {S} when the risk-free rate is {rf}?"
    score_target = grab(r"makes this score equal {N}", text)
    rf = grab(r"risk-free rate is {N}", text)

    # score = (R - rf) - lam * variance = S  ->  R = S + rf + lam * variance
    excess_return = score_target + lam * variance
    total_return = excess_return + rf

    # "Report a percentage."
    final = total_return * 100

    return {
        "final": final,
        "slots": {
            "weighted_volatility_a_checkpoint": weighted_vol_a,
            "weighted_volatility_b_checkpoint": weighted_vol_b,
        },
    }
