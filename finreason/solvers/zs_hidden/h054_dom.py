# FINANCE MODEL (h054) -- quick-ratio "convexity premium" from an inventory sale under two recovery states
#
# Givens (symbols):
#   Q   = quick assets before the sale, excluding inventory (USD)
#   B   = inventory carrying amount sold (USD)
#   f   = fraction of net proceeds retained as cash (stays in quick assets)
#   1-f = fraction of net proceeds that immediately repays current liabilities at par
#   rL  = low net-recovery rate;  rH = rL + spread (high rate)
#   p   = probability of the high state (low state has 1-p)
#   LH  = liabilities REMAINING AFTER high-state repayment (given instead of pre-sale liabilities)
#
# Mechanics:
#   Net proceeds in state s       : P_s = r_s * B   (recovery rate applied to inventory carrying amount)
#   Retained cash in state s      : C_s = f * P_s   (adds to quick assets; inventory leaves quick assets anyway,
#                                                    Q already excludes it)
#   Repayment in state s          : R_s = (1-f) * P_s
#   Post-sale quick assets        : A_s = Q + C_s
#   Implied pre-sale liabilities  : L0 = LH + R_H   (same in both states)
#   Post-sale liabilities         : L_s = L0 - R_s    (low: L0 - R_L ; high: LH)
#   State quick ratio             : q_s = A_s / L_s
#
# Convexity premium (expectation-order gap, positive by construction):
#   E[q]      = (1-p) q_L + p q_H                       (probability-weighted average of state ratios)
#   q(E)      = ((1-p) A_L + p A_H) / ((1-p) L_L + p L_H)   (ratio of probability-weighted assets / liabilities)
#   gap       = E[q] - q(E)                              (a plain ratio)
#   final     = 100 * gap  -> percentage points ("percent" unit)
#
# Checkpoints (all unrounded here, framework rounds):
#   1. low_state_retained_cash_checkpoint     = C_L = f * rL * B                 (USD)
#   2. incremental_retained_cash_checkpoint   = C_H - C_L = f * spread * B       (USD)
#   3. incremental_repayment_checkpoint       = R_H - R_L = (1-f) * spread * B   (USD)
#
# Overrides / notes: none of the stated rules override standard conventions; no intermediate rounding is used
# downstream (all checkpoints are independently rounded, so only exact values are carried).

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h054"


def solve(text: str, q: dict) -> dict:
    Q = grab(r"Quick assets before the sale, excluding inventory, are {N} USD", text)
    B = grab(r"inventory carrying amount {N} USD is sold", text)
    f = grab(r"fraction {N} of net proceeds remains as cash", text)
    rL = grab(r"low recovery rate is {N}", text)
    spread = grab(r"positive spread {N}", text)
    p = grab(r"high state occurs with probability {N}", text)
    LH = grab(r"the scenario gives {N} USD", text)

    rH = rL + spread

    # Net proceeds, retained cash, repayments by state
    P_L = rL * B
    P_H = rH * B
    C_L = f * P_L
    C_H = f * P_H
    R_L = (1 - f) * P_L
    R_H = (1 - f) * P_H

    # Implied pre-sale liabilities (common to both states)
    L0 = LH + R_H

    A_L = Q + C_L
    A_H = Q + C_H
    L_L = L0 - R_L
    L_H = L0 - R_H  # == LH

    q_L = A_L / L_L
    q_H = A_H / L_H

    avg_ratio = (1 - p) * q_L + p * q_H
    ratio_of_avgs = ((1 - p) * A_L + p * A_H) / ((1 - p) * L_L + p * L_H)

    gap = avg_ratio - ratio_of_avgs
    final = gap * 100

    return {
        "final": final,
        "slots": {
            "low_state_retained_cash_checkpoint": C_L,
            "incremental_retained_cash_checkpoint": C_H - C_L,
            "incremental_repayment_checkpoint": R_H - R_L,
        },
    }
