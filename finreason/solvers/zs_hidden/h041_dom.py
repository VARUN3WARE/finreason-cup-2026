# FINANCE MODEL (h041): two-period loan amortisation, solve for the unknown second payment.
#
#   B0  = initial outstanding principal
#   r   = effective rate per period (same in both periods, given as a decimal, e.g. 0.05 = 5%)
#   Interest accrues for the full period BEFORE the end-of-period payment (ordinary, arrears payment):
#       B1 = B0 * (1 + r) - P1            (balance immediately after the first-period payment)
#       B2 = B1 * (1 + r) - P2            (balance immediately after the second-period payment)
#   The target balance T is the balance immediately after payment 2, i.e. B2 = T.
#   Solve for the exact (unrounded) second payment:
#       P2 = B1 * (1 + r) - T
#   Final answer = P2 (USD, rounded half up to 2 dp by the framework).
#   Checkpoint "first_payment_balance_checkpoint" = B1 (USD) -- balance after the first-period payment.
#
# Conventions / overrides:
#   - rate is already a decimal fraction ("effective rate of 0.05"), NOT a percent; no division by 100.
#   - Payment amounts are NOT rounded inside the chain ("Define the target equality using the unrounded
#     exact payment"); everything is exact Fraction arithmetic and only the final display is rounded.
#   - P2 can be negative or zero if the target balance exceeds B1*(1+r); this is returned as-is (sign preserved).

from fractions import Fraction

from finreason.nums import grab, F

TEMPLATE_ID = "h041"


def solve(text: str, q: dict) -> dict:
    b0 = grab(r"outstanding principal of {N}", text)
    r = grab(r"effective rate of {N}", text)
    p1 = grab(r"pays {N} at the end of the first period", text)
    target = grab(r"leaves a balance of {N} immediately after that payment", text)

    growth = 1 + r
    b1 = b0 * growth - p1
    p2 = b1 * growth - target

    return {
        "final": p2,
        "slots": {
            "first_payment_balance_checkpoint": b1,
        },
    }
