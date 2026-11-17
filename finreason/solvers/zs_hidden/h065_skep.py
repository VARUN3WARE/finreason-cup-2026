"""Hidden cluster h065 -- chain-linked TWR vs Modified Dietz with a mid-period contribution
and a terminal cash distribution.  Final = (TWR - MD) in signed percentage points.

AMBIGUITIES CONSIDERED AND RESOLVED (skeptic pass)
--------------------------------------------------
1. Ending value vs terminal distribution.  "the post-distribution account value is V2 and a terminal
   cash distribution of D is paid at that same time; the ending value excludes that distribution".
   The distribution is cash returned to the investor at period end, so it is part of the period's
   return.  TWR: the second subperiod ends at the pre-distribution value V2 + D (the distribution is an
   external outflow at the subperiod boundary).  Modified Dietz: an external flow of -D at t=1 whose
   remaining-period weight is 0, so numerator = V2 - V0 - (C - D) = V2 + D - V0 - C and the
   denominator is unaffected.  Treating it consistently in BOTH measures is the only reading under
   which the two measures differ by a small timing effect (0.02 / -0.24 / -0.18 pp on the three
   instances); dropping D from one measure only produces ~18 pp gaps, which no "TWR minus Dietz"
   question would intend.  Ignoring D in both measures would discard investor cash and contradict the
   explicit "excludes that distribution" cue.  -> add D back in both.
2. Post-contribution start value of subperiod 2.  "Immediately before a contribution of C is added ...
   the account value is V1" and "no other external cash flows or valuation changes at the contribution
   instant" -> subperiod 2 starts at exactly V1 + C.
3. Subperiod returns.  r1 = V1/V0 - 1 (pre-contribution), r2 = (V2 + D)/(V1 + C) - 1
   (post-contribution).  Chain link: TWR = (1 + r1)(1 + r2) - 1.  Timing fraction t is irrelevant
   to TWR (only to Dietz).
4. Modified Dietz weight.  "using the contribution's remaining-period weight" -> w = 1 - t where t is
   the elapsed fraction ("after 0.6 of the period has elapsed").  Denominator = V0 + w*C.  The
   terminal distribution's weight is (1 - 1) = 0, so it contributes nothing to the denominator.
5. Elapsed fraction units.  Given as a fraction of the period (0.6, 0.5).  Defensive fallback: if the
   text says "percent" right after it, or the value exceeds 1, divide by 100.
6. Final quantity and sign.  "time-weighted return minus Modified Dietz return in signed percentage
   points" -> (TWR - MD) * 100, signed, no abs().  Final unit is percent -> return the pp number.
7. Checkpoint "period_one_return_checkpoint": "the exact-return checkpoint for the pre-contribution
   subperiod", unit ratio -> r1 = V1/V0 - 1 as a plain ratio (not 1 + r1, not percent).
8. No rounding anywhere inside the chain; all values returned unrounded (framework rounds).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h065"


def _elapsed_fraction(text: str) -> Fraction:
    m = re.search(
        r"after\s+(-?\d+(?:\.\d+)?(?:/\d+)?)\s*(percent|%)?\s*of the (?:measurement )?period",
        text,
        flags=re.S,
    )
    if m is None:
        raise ValueError("elapsed fraction not found")
    t = Fraction(m.group(1))
    if m.group(2) or t > 1:
        t = t / 100
    return t


def solve(text: str, q: dict) -> dict:
    v0 = grab(r"begins a measurement period at value {N}", text)
    contribution = grab(r"contribution of {N} is added", text)
    v_pre = grab(r"the account value is {N}", text)
    v_end_post_dist = grab(r"post-distribution account value is {N}", text)
    distribution = grab(r"terminal cash distribution of {N}", text)
    t = _elapsed_fraction(text)

    # Subperiod 1: start of period -> instant before the contribution.
    r1 = v_pre / v0 - 1
    # Subperiod 2: instant after the contribution -> period end, measured before the distribution.
    v_start2 = v_pre + contribution
    v_end_pre_dist = v_end_post_dist + distribution
    r2 = v_end_pre_dist / v_start2 - 1
    twr = (1 + r1) * (1 + r2) - 1

    # Modified Dietz: contribution weighted by the remaining fraction of the period; the terminal
    # distribution is an outflow with zero remaining weight.
    w_contribution = 1 - t
    w_distribution = Fraction(0)
    net_flow = contribution - distribution
    md_numerator = v_end_post_dist - v0 - net_flow
    md_denominator = v0 + w_contribution * contribution - w_distribution * distribution
    md = md_numerator / md_denominator

    diff_pp = (twr - md) * 100

    return {
        "final": diff_pp,
        "slots": {"period_one_return_checkpoint": r1},
    }
