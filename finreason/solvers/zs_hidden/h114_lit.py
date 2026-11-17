"""h114 -- minimum total-income threshold covering fixed cash outlays plus a savings share of income.

Literal transcription of the question, sentence by sentence:

  S1 "A household must cover essential outlays of E, planned discretionary outlays of D, and an
      emergency-reserve contribution of R while also saving s of total income in a separate savings
      commitment."
        -> three cash commitments (E, D, R) in USD and a fourth commitment = s * total income.
           Income Y meets all four commitments iff  Y >= E + D + R + s * Y.
  S2 "Compute the exact minimum total-income threshold that meets all four commitments."
        -> smallest Y with Y >= (E + D + R) + s * Y  =>  Y_min = (E + D + R) / (1 - s)   (needs s < 1).
  S3 "Determine feasibility from the unrounded exact threshold, then report that threshold in USD
      rounded half up to two decimal places; the displayed amount is a reporting approximation of the
      exact minimum."
        -> return the exact (unrounded) threshold; the framework applies the half-up 2dp rounding.

Checkpoint cash_needs_checkpoint: "combined cash commitments before solving for income"
        -> E + D + R (the dollar-denominated commitments; the savings commitment is a share of the
           still-unknown income, so it cannot be a cash amount before solving for income).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, grab

TEMPLATE_ID = "h114"


def _savings_share(text: str) -> Fraction:
    """'saving {N} of total income' -> ratio; tolerate a percent wording ('saving {N} percent of')."""
    m = re.search(rf"sav(?:e|es|ing)\s+({NUMBER})\s*(percent|%)?\s*of\s+(?:its\s+|the\s+|their\s+)?total income", text)
    if m is None:
        raise ValueError("savings share not found")
    value = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        value /= 100
    return value


def solve(text: str, q: dict) -> dict:
    # S1: the three cash commitments, in the order the text gives them (USD).
    essential_outlays = grab(r"essential outlays of {N}", text)
    discretionary_outlays = grab(r"discretionary outlays of {N}", text)
    emergency_reserve_contribution = grab(r"emergency-reserve contribution of {N}", text)
    # S1: the fourth commitment -- saving a share s of total income.
    savings_share = _savings_share(text)

    # Checkpoint: combined cash commitments before solving for income.
    cash_commitments = essential_outlays + discretionary_outlays + emergency_reserve_contribution

    # S2: total income Y meets all four commitments iff Y >= cash_commitments + savings_share * Y.
    #     Minimum threshold: Y_min * (1 - s) = cash_commitments.
    if savings_share >= 1:
        raise ValueError("savings share of at least 100% of income: no finite income threshold")
    income_threshold = cash_commitments / (1 - savings_share)

    # S3: feasibility is judged on the exact threshold -- at Y_min all four commitments are met exactly.
    assert income_threshold - (cash_commitments + savings_share * income_threshold) == 0

    return {
        "final": income_threshold,
        "slots": {"cash_needs_checkpoint": cash_commitments},
    }
