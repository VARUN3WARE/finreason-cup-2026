"""Zero-shot solver for hidden cluster h114 -- minimum household total-income threshold.

Structure (all 3 instances): fixed cash outlays E (essential), D (discretionary), R
(emergency-reserve contribution) plus a savings commitment equal to a fraction s of TOTAL
income.  Find the exact minimum income I* that meets all four commitments.

AMBIGUITY HUNT (resolved before coding; every resolution cites the question text):

A1  "saving 0.2 of total income": ratio or percent?
    -> RATIO.  The phrase is "<number> of total income" with no "percent" / "%" token, so 0.2
       means one fifth of income.  Defensive: if an instance ever writes "percent" or "%"
       directly after the number, divide by 100.
A2  Which base does the savings rate apply to -- gross income, or income left after outlays?
    -> GROSS ("of TOTAL income").  Savings commitment = s * I, where I is the income being
       solved for, so the equation is self-referential.
A3  What does the checkpoint "combined cash commitments before solving for income" denote?
    -> The three fixed-dollar outlays only: C = E + D + R.  The savings commitment is a function
       of the still-unknown income, so it cannot be part of a quantity reported "before solving
       for income".  "All four commitments" = three cash commitments + one savings commitment,
       which confirms the split.  Unit: usd, unscaled.
A4  Is the emergency-reserve contribution a cash commitment or part of the savings?
    -> Cash commitment.  It is listed with the two outlays as a fixed amount, and the savings is
       explicitly "a SEPARATE savings commitment".
A5  Minimum threshold: I must satisfy I >= E + D + R + s*I  <=>  I*(1 - s) >= C.
    "Meets" is non-strict and income is continuous, so the exact minimum is the equality point
    I* = C / (1 - s).  NOT C*(1 + s): that would apply the rate to the outlays, contradicting
    "of total income".
A6  "Determine feasibility from the unrounded exact threshold": feasibility is whether a finite,
    non-negative minimum exists, i.e. 1 - s > 0 and C >= 0, judged on the exact Fraction (never
    on the rounded display).  The answer spec is a plain USD decimal, so every instance must be
    feasible; an infeasible instance (s >= 1) raises instead of returning a meaningless number.
A7  Rounding: "use exact arithmetic through all intermediate steps, round only the final value".
    Both the final and the checkpoint are returned as UNROUNDED Fractions; the framework applies
    each result_spec's half-up 2-dp rendering.  The displayed checkpoint is never fed back in.
A8  Units: every amount is a plain USD figure (no thousands / millions scaling); the answer and
    the checkpoint are both "usd", so no conversion anywhere.
A9  Per-period vs annual: the text has no period structure -- a single static budget, so no
    annualisation or compounding is involved.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h114"

# Optional currency marker tolerated in front of an amount ("of USD 307.4" / "of $307.4").
_AMT = r"(?:USD\s*|\$\s*)?"


def _savings_rate(text: str) -> Fraction:
    """Fraction of total income committed to savings, as a plain ratio (A1 / A2)."""
    m = re.search(
        r"sav(?:ing|e|es)\s+" + _AMT + "(" + NUMBER + r")\s*(percent|%)?\s+of\s+(?:the\s+)?total\s+income",
        text,
        flags=re.S | re.I,
    )
    if m is None:
        raise ValueError("savings rate ('saving <N> of total income') not found")
    rate = F(m.group(1))
    if m.group(2):  # defensive only: none of the instances state a percent
        rate /= 100
    return rate


def solve(text: str, q: dict) -> dict:
    essential = grab(r"essential outlays of " + _AMT + "{N}", text)
    discretionary = grab(r"discretionary outlays of " + _AMT + "{N}", text)
    reserve = grab(r"emergency[-\s]reserve contribution of " + _AMT + "{N}", text)
    s = _savings_rate(text)

    # A3 / A4: combined cash commitments = the three fixed outlays (savings excluded).
    cash_needs = essential + discretionary + reserve

    # A5 / A6: I*(1 - s) = C  ->  I* = C / (1 - s); feasible only when 1 - s > 0 (exact test).
    retained = Fraction(1) - s
    if retained <= 0:
        raise ValueError(f"infeasible: savings rate {s} leaves no income to cover cash needs")
    threshold = cash_needs / retained
    if threshold < 0:
        raise ValueError("infeasible: negative income threshold")

    # A7: unrounded exact values; the framework renders half-up to 2 dp.
    return {"final": threshold, "slots": {"cash_needs_checkpoint": cash_needs}}
