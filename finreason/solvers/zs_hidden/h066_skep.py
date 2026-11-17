"""Cluster h066 -- ESG project: maximum initial investment that exactly meets a required ROI ratio.

Text structure (all 3 instances):
    "annual energy savings of E and annual water savings of W, while requiring annual maintenance
     cost of M. The full-horizon present-value multiplier for these recurring net benefits is k.
     Using ROI = (present value of net benefits minus initial investment) divided by initial
     investment, compute the maximum initial investment that exactly meets the required ROI ratio R."

Chain:
    annual net benefit  N  = E + W - M                      (checkpoint, usd)
    PV of net benefits  PV = k * N
    ROI = (PV - I) / I = R   ==>   PV = I * (1 + R)   ==>   I = PV / (1 + R)   (final, usd)

AMBIGUITY HUNT -- resolutions with textual evidence
-----------------------------------------------------
A1  What is the checkpoint "annual savings after maintenance"?
    -> E + W - M.  Both energy and water figures are called "annual ... savings"; maintenance is an
       "annual maintenance cost"; "savings after maintenance" = gross annual savings minus the annual
       maintenance cost.  Unit usd, unrounded (framework rounds half-up to 2 dp).
A2  Does the PV multiplier apply to gross savings (E + W) with maintenance treated separately, or to
    the net figure?
    -> To the net figure.  The multiplier is explicitly "for these recurring net benefits", and the
       maintenance cost is itself annual/recurring, so PV = k * (E + W - M).  Maintenance is NOT a
       one-off deduction outside the multiplier.
A3  Is the "multiplier" an annuity factor to be multiplied, or a rate to be discounted?
    -> A multiplier: "present-value multiplier ... is k" => PV = k * N.  No discount rate or horizon
       is given, so no annuity factor needs to be derived.
A4  Is the required ROI a ratio or a percent?
    -> Ratio.  The text says "required ROI ratio 1" / "4" / "2" with no "percent" or "%".  ROI = 1
       means 100 %.  The ROI definition given, (PV - I)/I, is a plain ratio.  Defensive handling: if a
       variant phrases it as "N percent" / "N%" the solver divides by 100 (never triggered here).
A5  "Maximum initial investment that exactly meets" -- is it an equality or an inequality bound?
    -> Equality.  ROI(I) = PV/I - 1 is strictly decreasing in I for PV > 0, so the largest I with
       ROI >= R is the unique I with ROI = R, i.e. I = PV / (1 + R).  "exactly meets" confirms.
A6  Which base does ROI divide by?
    -> Initial investment I (stated verbatim: "divided by initial investment"), not PV.
A7  Rounding inside the chain?
    -> None.  "use exact arithmetic through all intermediate steps, round only the final value".
       The checkpoint is returned unrounded (instance 3 has N = 102.425, an exact half at 2 dp, which
       the framework's half-up rounding renders as 102.43 -- exact Fractions make that certain).
A8  Sign / floor at zero?
    -> The text states no floor; the formula is returned as-is.  All 3 instances have positive net
       benefit, so I > 0.  (If N <= 0 the formula yields I <= 0; no rule in the text overrides it.)
A9  Per-period vs annual?
    -> Everything is annual and the multiplier is "full-horizon", so no period conversion is needed.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, grab

TEMPLATE_ID = "h066"

_USD = r"(?:USD\s*|\$\s*)?"


def _roi_ratio(text: str) -> Fraction:
    """Required ROI as a plain ratio; divides by 100 only if the number is explicitly a percent."""
    rx = rf"required ROI(?: ratio)?(?: of)?\s*{_USD}({NUMBER})\s*(percent|%)?"
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError("required ROI not found")
    r = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        r /= 100
    return r


def solve(text: str, q: dict) -> dict:
    energy = grab(rf"annual energy savings of {_USD}{{N}}", text)
    water = grab(rf"annual water savings of {_USD}{{N}}", text)
    maint = grab(rf"annual maintenance cost of {_USD}{{N}}", text)
    mult = grab(r"present-value multiplier for these recurring net benefits is {N}", text)
    roi = _roi_ratio(text)

    # A1: annual net benefit = gross annual savings minus annual maintenance cost.
    net_annual = energy + water - maint

    # A2/A3: full-horizon PV of the recurring net benefits.
    pv_net = mult * net_annual

    # A5/A6: ROI = (PV - I) / I = R  =>  I = PV / (1 + R).
    max_investment = pv_net / (1 + roi)

    return {
        "final": max_investment,
        "slots": {"annual_net_benefit_checkpoint": net_annual},
    }
