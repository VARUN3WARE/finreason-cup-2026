"""Cluster h014 -- scenario-defined mean-variance score: solve for total portfolio return.

Structure (identical across the 3 instances; only numbers and the branch outcome differ):
  * Asset A weight w_A given; Asset B "receives the complementary weight"  ->  w_B = 1 - w_A.
  * Return volatilities sigma_A, sigma_B given as plain ratios.
  * A risk engine supplies a BASE and a STRESS "weighted covariance cross-term contribution";
    "each already equals twice the product of both portfolio weights and the regime covariance",
    i.e. each number IS 2 * w_A * w_B * Cov  ->  it is added to the variance as-is (no further
    scaling by 2 or by the weights).
  * Branch: "Use the stress contribution when X is at least Y, and otherwise use the base
    contribution"  ->  stress iff X >= Y (non-strict; instance 2 is an exact tie 0.5 vs 0.5 and
    therefore selects STRESS).  Instance 3 (0.2 vs 0.5) selects BASE.
  * Portfolio variance = (w_A*sigma_A)^2 + (w_B*sigma_B)^2 + selected contribution.
  * Score = portfolio excess return - lambda * variance = (R_p - r_f) - lambda * var.
  * Question: which total portfolio return R_p makes score == S given r_f?
        R_p = S + lambda * var + r_f
    "Report a percentage"  ->  final = R_p * 100 (answer_spec unit = percent).

AMBIGUITY RESOLUTIONS
  1. "weighted volatility" checkpoints (unit ratio, 6 dp): the text calls the variance terms
     "squared weight-scaled volatilities", so the weight-scaled volatility itself is w * sigma
     (NOT (w*sigma)^2 and NOT w*sigma^2).  Checkpoint A = w_A*sigma_A, checkpoint B = w_B*sigma_B.
  2. Contribution scaling: already 2*w_A*w_B*Cov -> used directly.
  3. Comparison "at least" -> >= (tie goes to stress).  Defensive parsing of other comparators
     ("more than"/"exceeds"/"greater than" -> >, "at most" -> <=, "below"/"less than" -> <) is
     included but all 3 instances use "is at least".
  4. Risk-free rate and score target are given as ratios (0.02, 0.05), not percents -> no /100.
     Instances with "0" for both are handled (the number regex matches "0").
  5. Units: the final answer is a percent -> R_p * 100.  Checkpoints are ratios -> no scaling.
  6. lambda parsed from "minus {N} times variance"; excess return = R_p - r_f (standard meaning,
     and the question itself states the risk-free rate for that purpose).
  7. No rounding anywhere inside the computation; everything returned unrounded as Fractions.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab, grab_all

TEMPLATE_ID = "h014"


def _select_stress(text: str) -> bool:
    """Evaluate 'Use the stress contribution when X <cmp> Y'."""
    m = re.search(
        rf"[Uu]se the stress contribution when ({NUMBER}) (is at least|is at most|is more than|"
        rf"is greater than|exceeds|is below|is less than|is strictly greater than|"
        rf"is strictly less than|equals|is equal to) ({NUMBER})",
        text,
        flags=re.S,
    )
    if m is None:
        raise ValueError("stress condition not found")
    x = F(m.group(1))
    cmp_ = m.group(2)
    y = F(m.group(3))
    if cmp_ == "is at least":
        return x >= y
    if cmp_ == "is at most":
        return x <= y
    if cmp_ in ("is more than", "is greater than", "exceeds", "is strictly greater than"):
        return x > y
    if cmp_ in ("is below", "is less than", "is strictly less than"):
        return x < y
    if cmp_ in ("equals", "is equal to"):
        return x == y
    raise ValueError(f"unknown comparator {cmp_!r}")


def solve(text: str, q: dict) -> dict:
    w_a = grab(r"Asset A has portfolio weight {N}", text)
    w_b = Fraction(1) - w_a  # "Asset B receives the complementary weight"

    sig_a, sig_b = grab_all(r"return volatilities are {N} and {N}", text)

    c_base, c_stress = grab_all(
        r"base weighted covariance cross-term contribution {N} and stress contribution {N}", text
    )

    contribution = c_stress if _select_stress(text) else c_base

    lam = grab(r"minus {N} times variance", text)

    target_score, r_f = grab_all(r"score equal {N} when the risk-free rate is {N}", text)

    wv_a = w_a * sig_a  # weight-scaled volatility of Asset A (ratio)
    wv_b = w_b * sig_b  # weight-scaled volatility of Asset B (ratio)

    variance = wv_a**2 + wv_b**2 + contribution

    # score = (R_p - r_f) - lam * variance  ==  target_score   =>   R_p = target + lam*var + r_f
    r_p = target_score + lam * variance + r_f

    return {
        "final": r_p * 100,  # percent
        "slots": {
            "weighted_volatility_a_checkpoint": wv_a,
            "weighted_volatility_b_checkpoint": wv_b,
        },
    }
