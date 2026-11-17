# FINANCE MODEL (h100) -- Modified Dietz return with a mid-period contribution and a terminal distribution.
#
# Notation: BMV = beginning value; C = contribution added at elapsed fraction t of the period;
#           EMV_post = stated post-distribution ending value; D = terminal cash distribution paid at period end.
#
# Modified Dietz (standard):
#     R = (EMV - BMV - sum CF_i) / (BMV + sum w_i * CF_i),   w_i = (T - t_i)/T = 1 - t_i  (fraction of period remaining)
#   with CF_i signed external flows (contributions positive, withdrawals/distributions negative).
#
# How each number enters:
#   * BMV: starting value, full weight 1 in the denominator (capital base).
#   * C at elapsed fraction t: external inflow, +C in net flow; denominator weight (1 - t) -- the text says to weight
#     by the fraction of the period remaining.  Weighted contribution = C * (1 - t)  (the checkpoint, in USD).
#   * D: external outflow (a terminal distribution leaves the account), -D in net flow.  The text gives it ZERO weight in
#     the denominator (paid at the very end, remaining fraction = 0), so it contributes nothing to the capital base.
#   * "the ending value excludes that distribution": the ending value 1174 is net of D, i.e. EMV_post = value after the
#     distribution left.  Economic gain = EMV_post - BMV - (C - D) = (EMV_post + D) - BMV - C.  The distribution is
#     therefore added back to the numerator via the net external flow (it is part of the investment gain delivered to
#     the holder), NOT dropped.
#   * No other flows.
#   Gain      = EMV_post - BMV - (C - D)
#   Capital   = BMV + C*(1 - t)  (+ D * 0)
#   ROI (percent) = 100 * Gain / Capital, round half-up 2 dp (framework).
#   Checkpoint weighted_contribution = C*(1 - t), usd, rounded 4 dp by the framework.
#
# No overrides of standard convention beyond the stated weighting.

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h100"


def solve(text: str, q: dict) -> dict:
    bmv = grab(r"begins a measurement period at value {N}", text)
    contrib = grab(r"A contribution of {N} is added", text)
    t = grab(r"after {N} of the period has elapsed", text)
    emv_post = grab(r"post-distribution account value is {N}", text)
    dist = grab(r"terminal cash distribution of {N} is paid", text)

    weight = 1 - t                       # fraction of the period remaining
    weighted_contrib = contrib * weight
    net_flow = contrib - dist            # external flows: +contribution, -terminal distribution
    gain = emv_post - bmv - net_flow
    capital = bmv + weighted_contrib     # terminal distribution has zero denominator weight
    roi_pct = gain / capital * 100

    return {"final": roi_pct, "slots": {"weighted_contribution_checkpoint": weighted_contrib}}
