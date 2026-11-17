"""Cluster h100 -- Modified Dietz ROI with one intra-period contribution and a
terminal cash distribution (skeptical / ambiguity-hunting analyst).

AMBIGUITIES CONSIDERED AND HOW THEY WERE RESOLVED
--------------------------------------------------
A1. Formula.  Standard Modified Dietz:
        R = (EMV - BMV - sum CF_i) / (BMV + sum W_i * CF_i)
    where CF_i are SIGNED external flows (inflow +, outflow -) and W_i is the
    fraction of the period remaining after flow i.  The text explicitly says
    "Under the standard Modified Dietz convention", so no simple-Dietz /
    mid-point weighting is used.

A2. Contribution weight.  "weight the contribution by the fraction of the
    period remaining" and the flow occurs "after x of the period has elapsed"
    -> W_C = 1 - x.  x is given as a plain fraction of the period (0.25, 0.5,
    0.75), not a percent.  (Defensive: if a future wording says "x percent of
    the period", the parser divides by 100.)

A3. Role of the terminal distribution D.
    - "There are no OTHER external cash flows" classifies D as an external
      cash flow.
    - "the ending value excludes that distribution" -> D has left the account
      and is NOT inside EMV, so it must be an OUTFLOW: CF_D = -D.
    - "give the terminal distribution zero denominator weight" -> W_D = 0
      (consistent with a flow at t = 1, fraction remaining = 0).
    Hence  sum CF = C - D,  numerator = EMV - BMV - C + D,
           denominator = BMV + (1 - x) * C + 0 * (-D) = BMV + (1 - x) * C.
    Cross-check: this is algebraically identical to the other consistent
    reading "use the PRE-distribution ending value EMV + D with no terminal
    flow at all".  The two readings that would differ -- ignoring D entirely,
    or treating D as an inflow -- both contradict the sentences above
    (a distribution paid out to the investor is part of the return earned).

A4. Checkpoint "time-weighted contribution used in the Modified Dietz capital
    base" (unit usd, 4 dp).  The capital base is BMV + W_C * C; the
    time-weighted contribution is the term W_C * C that is ADDED to BMV, not
    the whole base.  Note that "sum of all weighted flows" gives the same
    number, because the distribution's weight is zero, so this checkpoint is
    unambiguous between those two phrasings.  It is NOT BMV + W_C * C.

A5. Units.  Final answer is "as a percentage" with unit percent -> R * 100,
    returned unrounded (framework rounds half-up to 2 dp).  Checkpoint is in
    USD, returned unrounded (framework rounds to 4 dp).  Nothing in the chain
    is rounded internally (no whole-unit / cents rule is stated).

A6. Signs.  All given amounts are positive in these instances; the signed
    NUMBER regex would carry a negative sign through correctly if one
    appeared.  A negative numerator (loss) is simply a negative percent.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, grab_all, F, NUMBER

TEMPLATE_ID = "h100"


def _fraction_elapsed(text: str) -> Fraction:
    """Fraction of the period elapsed when the contribution is made.

    Accepts "after 0.25 of the period has elapsed" and, defensively,
    "after 25 percent of the period has elapsed" / "after 25% of the period".
    """
    m = re.search(
        r"after\s+(" + NUMBER + r")\s*(percent|%)?\s+of\s+the\s+period",
        text,
        flags=re.S,
    )
    if m is None:
        raise ValueError("could not find the contribution timing")
    x = F(m.group(1))
    if m.group(2):
        x = x / 100
    return x


def solve(text: str, q: dict) -> dict:
    # Beginning market value.
    bmv = grab(r"begins a measurement period at value {N}", text)

    # Intra-period contribution (external inflow) and its timing.
    contribution = grab(r"contribution of {N} is added", text)
    elapsed = _fraction_elapsed(text)
    weight = 1 - elapsed  # fraction of the period remaining (A2)

    # Ending value AFTER the distribution has been paid out, and the terminal
    # distribution itself (external outflow at t = 1, weight 0) (A3).
    emv_post = grab(r"post-distribution account value is {N}", text)
    distribution = grab(r"terminal cash distribution of {N}", text)

    # Signed external flows.
    flows = [
        (contribution, weight),  # inflow, weighted by time remaining
        (-distribution, Fraction(0)),  # outflow at period end, zero weight
    ]
    net_flow = sum(cf for cf, _ in flows)
    weighted_flows = sum(cf * w for cf, w in flows)

    # Checkpoint: the time-weighted contribution term in the capital base (A4).
    weighted_contribution = contribution * weight
    assert weighted_contribution == weighted_flows  # D's weight is zero

    numerator = emv_post - bmv - net_flow  # = EMV + D - BMV - C
    denominator = bmv + weighted_flows  # = BMV + (1 - x) * C
    roi = numerator / denominator

    return {
        "final": roi * 100,  # percent (A5)
        "slots": {
            "weighted_contribution_checkpoint": weighted_contribution,
        },
    }
