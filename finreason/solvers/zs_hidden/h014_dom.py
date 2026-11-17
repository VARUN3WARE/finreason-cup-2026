# FINANCE MODEL (two-asset mean-variance score, solved for the required total return)
#
# Given:
#   w_A  = weight of Asset A, w_B = 1 - w_A (complementary weight)
#   s_A, s_B = return volatilities (standard deviations) of A and B
#   Base / stress "weighted covariance cross-term contribution": each ALREADY equals
#       2 * w_A * w_B * (regime covariance)   -> used as-is, no further weight scaling.
#   Selection rule: use the STRESS contribution when (x >= y) (non-strict "at least"),
#       otherwise the BASE contribution.
#   Weighted volatility of asset i = w_i * s_i   (the "weight-scaled volatility"; these are the
#       two checkpoints, in plain ratio units).
#   Portfolio variance  V = (w_A s_A)^2 + (w_B s_B)^2 + selected_contribution
#   Score = (R - r_f) - lambda * V, where R is total portfolio return, r_f the risk-free rate,
#       excess return = R - r_f, lambda the stated risk-aversion coefficient ("minus L times variance").
#   Solve Score = target for R:
#       R = r_f + target + lambda * V
#   Final answer reported as percent: 100 * R.
#
# Conventions / overrides: none beyond the text. Everything in decimals (ratios), exact Fractions.
# Checkpoints are the weighted volatilities w_A*s_A and w_B*s_B as ratios (not percent).

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h014"


def solve(text: str, q: dict) -> dict:
    w_a = grab(r"Asset A has portfolio weight {N}", text)
    w_b = 1 - w_a
    s_a, s_b = grab_all(r"return volatilities are {N} and {N}", text)
    base_c = grab(r"base weighted covariance cross-term contribution {N}", text)
    stress_c = grab(r"stress contribution {N}", text)
    x, y = grab_all(r"Use the stress contribution when {N} is at least {N}", text)
    lam = grab(r"minus {N} times variance", text)
    target = grab(r"score equal {N} when", text)
    rf = grab(r"risk-free rate is {N}", text)

    contrib = stress_c if x >= y else base_c

    wv_a = w_a * s_a
    wv_b = w_b * s_b
    var = wv_a ** 2 + wv_b ** 2 + contrib

    # score = (R - rf) - lam * var = target
    total_return = rf + target + lam * var
    final = total_return * 100

    return {
        "final": final,
        "slots": {
            "weighted_volatility_a_checkpoint": wv_a,
            "weighted_volatility_b_checkpoint": wv_b,
        },
    }
