"""h065: chain-linked TWR (one mid-period contribution, terminal distribution)
minus Modified Dietz return, in signed percentage points."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h065"


def solve(text: str, q: dict) -> dict:
    bmv = grab(r"begins a measurement period at value {N}", text)
    contrib = grab(r"contribution of {N} is added", text)
    frac_elapsed = grab(r"after {N} of the period has elapsed", text)
    pre_value = grab(r"the account value is {N}", text)
    emv = grab(r"post-distribution account value is {N}", text)
    dist = grab(r"terminal cash distribution of {N}", text)

    # Subperiod 1: start -> immediately before contribution.
    r1 = pre_value / bmv - 1
    # Subperiod 2: post-contribution value -> end value with the end-of-period
    # distribution added back (it is paid at period end, ending value excludes it).
    start2 = pre_value + contrib
    end2 = emv + dist
    r2 = end2 / start2 - 1
    twr = (1 + r1) * (1 + r2) - 1

    # Modified Dietz: contribution weighted by remaining fraction of the period;
    # terminal distribution has zero remaining weight.
    w_c = 1 - frac_elapsed
    w_d = Fraction(0)
    net_cf = contrib - dist
    gain = emv - bmv - net_cf
    denom = bmv + contrib * w_c - dist * w_d
    md = gain / denom

    final = (twr - md) * 100
    return {"final": final, "slots": {"period_one_return_checkpoint": r1}}
