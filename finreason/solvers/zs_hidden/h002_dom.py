# FINANCE MODEL (h002) -- loss-severity alignment diagnostic for a fraud-reimbursement schedule
#
# States (mutually exclusive, exhaustive), conditional on one fraud event:
#   minor    : p1 = P(minor)                       (given directly, 0.2)
#   moderate : p2 = (1 - p1) * q,  q = P(moderate | not minor)   (given, 0.5)
#   severe   : p3 = (1 - p1) * (1 - q)   (the remainder "otherwise the severe state occurs")
# Gross fraud losses L1, L2, L3 (USD) and reimbursement fractions (rates) r1, r2, r3.
#
# Quantities:
#   Expected gross loss            E[L]   = sum p_i L_i
#   Actual expected reimbursement  E[R]   = sum p_i L_i r_i
#   Probability-weighted mean rate rbar   = sum p_i r_i        (weights are state probabilities,
#                                                               NOT loss weights -- text says
#                                                               "probability-weighted mean reimbursement rate")
#   Flat-rate benchmark            B      = rbar * E[L]        ("applying the mean rate uniformly to expected gross loss")
#   Final answer                   E[R] - B = sum p_i L_i r_i - (sum p_i r_i)(sum p_i L_i) = Cov(L, r)  (USD)
#     positive => higher-loss states get higher rates than a flat rate; negative => lower.
#
# Checkpoints (USD, unrounded, framework rounds to 4 dp):
#   moderate_weighted_loss_checkpoint = p2 * L2   (probability-weighted moderate-state GROSS loss, before reimbursement)
#   severe_weighted_loss_checkpoint   = p3 * L3
#
# No overrides of standard conventions; no intermediate rounding (text: "exact arithmetic ... round the final amount").

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h002"


def solve(text: str, q: dict) -> dict:
    p_minor = grab(r"minor state has probability {N}", text)
    q_mod = grab(r"moderate state has probability {N}", text)
    L1, L2, L3 = grab_all(r"gross fraud losses are {N}, {N}, and {N} USD", text)
    r1, r2, r3 = grab_all(r"reimburses fractions {N}, {N}, and {N}", text)

    p1 = p_minor
    p2 = (1 - p1) * q_mod
    p3 = (1 - p1) * (1 - q_mod)
    assert p1 + p2 + p3 == 1

    ps = [p1, p2, p3]
    Ls = [L1, L2, L3]
    rs = [r1, r2, r3]

    exp_loss = sum(p * L for p, L in zip(ps, Ls))
    exp_reimb = sum(p * L * r for p, L, r in zip(ps, Ls, rs))
    mean_rate = sum(p * r for p, r in zip(ps, rs))
    benchmark = mean_rate * exp_loss
    diff = exp_reimb - benchmark

    return {
        "final": diff,
        "slots": {
            "moderate_weighted_loss_checkpoint": p2 * L2,
            "severe_weighted_loss_checkpoint": p3 * L3,
        },
    }
