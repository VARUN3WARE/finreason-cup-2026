# FINANCE MODEL (h009): two-route transfer net receipt with a threshold routing rule.
#
# Inputs: transfer amount T (USD); Network A: fee ratio fA, fixed fee cA;
#         Network B: fee ratio fB, fixed fee cB, bonus ratio bB; threshold H for A.
#
# Network A receipt:   A = T*(1 - fA) - cA          (proportional fee first, then fixed fee)
# Network B receipt:
#     B1 = T*(1 - fB)        <- checkpoint "after proportional fee, before fixed fee and bonus"
#     B2 = B1 - cB           (fixed fee deducted from post-ratio-fee amount)
#     B  = B2*(1 + bB)       (bonus ratio increases the post-fee amount: multiplicative uplift)
# Routing rule (unrounded intermediates): use A if A >= H (inclusive of equality), else B.
# Final answer = selected receipt (unrounded; framework rounds half up to 2 dp in USD).
# Notes / conventions:
#   - "fee ratio r" is a fraction of the amount (0.4 = 40%), not a percent; no rescaling.
#   - No rounding inside the computation; both candidates computed before the rule is applied.
#   - Checkpoint is always Network B's value T*(1-fB) regardless of which network is selected.
#   - No floor at zero is stated, so none is applied.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h009"


def solve(text: str, q: dict) -> dict:
    T = grab(r"A transfer of {N} USD", text)
    fA = grab(r"Network A deducts fee ratio {N}", text)
    cA = grab(r"Network A deducts fee ratio {N} and then fixed fee {N} USD", text, group=2)
    fB = grab(r"Network B deducts fee ratio {N}", text)
    cB = grab(r"Network B deducts fee ratio {N}, then fixed fee {N} USD", text, group=2)
    bB = grab(r"bonus ratio {N}", text)
    H = grab(r"use Network A if its net receipt is at least {N} USD", text)

    A = T * (1 - fA) - cA
    B1 = T * (1 - fB)
    B = (B1 - cB) * (1 + bB)

    final = A if A >= H else B
    return {"final": final, "slots": {"network_b_after_ratio_fee_checkpoint": B1}}
