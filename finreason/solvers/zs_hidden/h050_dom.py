# FINANCE MODEL (h050): two-part-tariff comparison of remittance / transfer plans.
#
# Inputs
#   V  = expected transfer volume per month (USD)
#   n  = number of transfers per month
#   M  = number of months in the horizon
# Each plan P has: proportional rate r_P (a decimal ratio, 0.01 = 1% of volume),
#   per-transfer fee f_P (USD per transfer), monthly subscription s_P (USD per month),
#   one-time setup fee u_P (USD, charged exactly ONCE at account opening).
#
# Horizon aggregates
#   total volume  = V * M            (checkpoint 1, USD, rendered to 4 dp)
#   total count   = n * M            (checkpoint 2, dimensionless)
#
# Plan total cost over horizon
#   cost_P = u_P + s_P * M + r_P * (V * M) + f_P * (n * M)
#   (rate applies to the whole horizon volume; fee to the whole horizon count;
#    subscription is per month; setup is once -- NOT multiplied by months or transfers.)
#
# Final answer = Plan A savings relative to Plan B = cost_B - cost_A   (signed, USD,
#   positive when A is cheaper). Unrounded exact value is returned; the framework
#   rounds half-up to 2 dp.
#
# Overrides / conventions noted: rate is a plain ratio (0.01 -> 1%), not percent-number;
#   no discounting; setup fees may have 3 decimals (e.g. 50.775) -> exact Fractions.

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab, grab_all

TEMPLATE_ID = "h050"


def solve(text: str, q: dict) -> dict:
    V, n, M = grab_all(
        r"monthly transfer volume {N} and {N} transfers per month for {N} months", text
    )

    # Plan A: explicit labels.
    rA, fA, sA, uA = grab_all(
        r"Plan A charges proportional transfer rate {N}, fee {N} per transfer, "
        r"monthly subscription {N}, and one-time setup fee {N}",
        text,
    )
    # Plan B: terse list in the same order (rate, per-transfer fee, subscription, setup).
    rB, fB, sB, uB = grab_all(
        r"Plan B charges {N}, {N}, {N}, and one-time setup fee {N}", text
    )

    total_volume = V * M
    total_count = n * M

    def cost(r, f, s, u):
        return u + s * M + r * total_volume + f * total_count

    cost_a = cost(rA, fA, sA, uA)
    cost_b = cost(rB, fB, sB, uB)
    savings = cost_b - cost_a

    return {
        "final": savings,
        "slots": {
            "horizon_volume_checkpoint": total_volume,
            "horizon_count_checkpoint": total_count,
        },
    }
