# FINANCE MODEL (h084) -- degree of financial leverage from reconstructed EBIT
#
# Given, for a single period (all amounts and rates on the same period basis):
#   EBT  = earnings before tax (positive), already AFTER deducting all modeled interest
#   D_A, r_A = tranche A debt principal (USD) and period interest rate (decimal, 0.1 = 10%)
#   D_B, r_B = tranche B debt principal (USD) and period interest rate (decimal)
#
# Simplified fixed-interest model: no other non-operating items, no preferred dividends,
# no tax adjustments.  Interest is simple, exact-period:  I_X = D_X * r_X   (no compounding,
# no day-count; rates are already stated as decimals, NOT percents).
#
#   Checkpoint 1 (tranche_a_interest_checkpoint, USD) = I_A = D_A * r_A
#   Checkpoint 2 (tranche_b_interest_checkpoint, USD) = I_B = D_B * r_B
#   EBIT = EBT + I_A + I_B            (interest added back to pre-tax earnings)
#   DFL  = EBIT / EBT                 (final answer, plain multiple, > 1 since interest > 0)
#
# Conventions / overrides: none; rates are decimals as stated ("rate 0.1"), so no /100.
# Everything is exact Fraction arithmetic; the framework rounds each value half-up to
# 4 decimals independently (checkpoints are not fed into the final calculation in rounded form).

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h084"


def solve(text: str, q: dict) -> dict:
    ebt = grab(r"earnings before tax of {N} USD", text)
    d_a = grab(r"Tranche A debt is {N} USD at rate {N}", text, 1)
    r_a = grab(r"Tranche A debt is {N} USD at rate {N}", text, 2)
    d_b = grab(r"tranche B debt is {N} USD at rate {N}", text, 1)
    r_b = grab(r"tranche B debt is {N} USD at rate {N}", text, 2)

    int_a = d_a * r_a
    int_b = d_b * r_b
    ebit = ebt + int_a + int_b
    dfl = ebit / ebt

    return {
        "final": Fraction(dfl),
        "slots": {
            "tranche_a_interest_checkpoint": int_a,
            "tranche_b_interest_checkpoint": int_b,
        },
    }
