# FINANCE MODEL (h085): current loan vs refinance, two-period amortisation roll-forward.
#
# Both paths share the same two equal-length periods. Let P = outstanding principal today.
#
# Current loan:
#   opening balance      B0_c = P
#   effective rate per period r_c, level payment p_c at each period END
#   interest accrues BEFORE the payment (ordinary annuity / arrears payment):
#       B1_c = B0_c * (1 + r_c) - p_c          (balance after first payment)
#       B2_c = B1_c * (1 + r_c) - p_c          (balance after second payment)
#
# Refinance:
#   opening balance      B0_r = P + fee         (fee is capitalised into the opening balance,
#                                                i.e. financed, not paid in cash)
#   effective rate per period r_r, payment p_r at each period end
#       B1_r = B0_r * (1 + r_r) - p_r
#       B2_r = B1_r * (1 + r_r) - p_r
#
# Final answer = B2_c - B2_r  (signed, current minus refinance), USD, 2dp half-up.
# Checkpoint 1 = B1_c, checkpoint 2 = B1_r (balances after their respective first payments).
#
# Conventions / overrides noted:
#  - The "effective rate" is already per period, so no compounding conversion is needed.
#  - No floor at zero is stated, so none is applied (balances stay positive in all instances anyway).
#  - All quantities are exact Fractions; nothing is rounded inside the computation.
#  - Each loan's rate/payment is attached to it by anchoring on "current loan uses" / "then uses".

from fractions import Fraction

from finreason.nums import grab_all, grab

TEMPLATE_ID = "h085"


def solve(text: str, q: dict) -> dict:
    principal = grab(r"outstanding principal of {N}", text)

    # Each loan's rate and payment are anchored on its own sentence.
    r_c, p_c = grab_all(
        r"current loan uses an effective rate of {N} and a payment of {N} at each period end", text)
    fee = grab(r"capitalizes a fee of {N} into its opening balance", text)
    r_r, p_r = grab_all(
        r"then uses an effective rate of {N} and a payment of {N} at each period end", text)

    # Current loan roll-forward (interest accrues before each end-of-period payment)
    b0_c = principal
    b1_c = b0_c * (1 + r_c) - p_c
    b2_c = b1_c * (1 + r_c) - p_c

    # Refinance roll-forward (fee capitalised into opening balance)
    b0_r = principal + fee
    b1_r = b0_r * (1 + r_r) - p_r
    b2_r = b1_r * (1 + r_r) - p_r

    final = b2_c - b2_r

    return {
        "final": final,
        "slots": {
            "current_first_payment_balance_checkpoint": b1_c,
            "refinance_first_payment_balance_checkpoint": b1_r,
        },
    }
