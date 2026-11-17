"""h116 -- maximum COGS consistent with a required operating margin.

Question shape:
    "Given projected revenue of R, operating expenses of OPEX, and a required
     operating margin of M, determine the maximum COGS that can be incurred
     while exactly meeting the margin requirement. Report the result in USD
     millions."

Checkpoint (position 1): target_margin_ratio_checkpoint
    "Convert the required operating margin from percent to a ratio"  [ratio, 6 dp]
Final: maximum COGS in usd_million [2 dp half-up].

AMBIGUITIES CONSIDERED AND RESOLUTIONS
--------------------------------------
A1. What "operating margin" means.
    Resolved: operating margin = operating income / revenue, with
    operating income = revenue - COGS - operating expenses (standard
    definition). The text supplies exactly the three components revenue,
    operating expenses and COGS, and asks for COGS as the residual that makes
    the margin hold "exactly", so
        COGS_max = R * (1 - m) - OPEX.
    Rejected: (a) gross-margin reading (R - COGS)/R, which would leave the
    stated operating expenses unused; (b) "operating expenses" inclusive of
    COGS, under which COGS would not be pinned down by the margin at all;
    (c) a markup-on-cost reading, which is not what "operating margin" means.

A2. Percent vs ratio for the margin input (24.60253 / 34.16355 / 36).
    Resolved: percent. The checkpoint description literally says "Convert the
    required operating margin from percent to a ratio", so the checkpoint is
    M/100 and that same ratio is used downstream.

A3. Whether the 6-dp rounded checkpoint feeds the final.
    Resolved: no -- the exact ratio M/100 is used; only the framework rounds.
    (Checked: for all three instances the 2-dp final is the same either way,
    so this choice is not load-bearing here.)

A4. Units of the inputs.
    Resolved: revenue and operating expenses are bare numbers in a problem
    that says "Report the result in USD millions"; they are taken as already
    being in USD millions, so no scaling is applied and the final is in
    USD millions.

A5. "Maximum COGS ... while exactly meeting the margin requirement".
    Resolved: the algebraic residual, with no floor at zero and no
    whole-unit rounding (nothing in the text asks for either). All three
    instances yield a positive value anyway.

A6. Half-up ties.
    Instance 3's final is exactly 21.265 (-> 21.27) and instance 2's ratio is
    exactly 0.3416355 (-> 0.341636); exact Fraction arithmetic keeps these
    ties deterministic, which float arithmetic would not.
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h116"

_AMT = r"(?:USD\s*|\$\s*)?{N}"


def solve(text: str, q: dict) -> dict:
    revenue = grab(r"revenue\s+of\s+" + _AMT, text)
    opex = grab(r"operating\s+expenses\s+of\s+" + _AMT, text)
    margin_pct = grab(r"operating\s+margin\s+of\s+" + _AMT, text)

    # Checkpoint 1: required operating margin as a ratio (percent / 100).
    margin_ratio: Fraction = margin_pct / 100

    # Operating income needed = revenue * margin; gross profit needed =
    # operating income + operating expenses; COGS = revenue - gross profit.
    # Equivalently COGS_max = revenue * (1 - m) - opex.
    required_operating_income = revenue * margin_ratio
    max_cogs = revenue - opex - required_operating_income

    return {
        "final": max_cogs,
        "slots": {"target_margin_ratio_checkpoint": margin_ratio},
    }
