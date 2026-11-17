"""h014: mean-variance score -- required total portfolio return.

wA given, wB = 1 - wA. Weighted volatilities wA*sA, wB*sB.
Cross-term: stress contribution if <x> is at least <y>, else base contribution
(each already equals 2*wA*wB*cov, so it is added as-is).
Variance = (wA sA)^2 + (wB sB)^2 + selected contribution.
Score = (Rp - rf) - lambda * variance = target  =>  Rp = target + rf + lambda * variance.
Final reported in percent.
"""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h014"


def solve(text: str, q: dict) -> dict:
    wa = grab(r"Asset A has portfolio weight {N}", text)
    wb = 1 - wa
    sa, sb = grab_all(r"return volatilities are {N} and {N}", text)
    base = grab(r"base weighted covariance cross-term contribution {N}", text)
    stress = grab(r"stress contribution {N}", text)
    x, y = grab_all(r"Use the stress contribution when {N} is at least {N}", text)
    lam = grab(r"excess return minus {N} times variance", text)
    target = grab(r"score equal {N}", text)
    rf = grab(r"risk-free rate is {N}", text)

    wva = wa * sa
    wvb = wb * sb
    contrib = stress if x >= y else base
    var = wva ** 2 + wvb ** 2 + contrib
    rp = target + rf + lam * var

    return {
        "final": rp * 100,
        "slots": {
            "weighted_volatility_a_checkpoint": wva,
            "weighted_volatility_b_checkpoint": wvb,
        },
    }
