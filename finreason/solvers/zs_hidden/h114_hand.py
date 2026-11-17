"""h114: minimum total-income threshold covering fixed outlays plus a savings share of income.

Structure: essential outlays E, planned discretionary outlays D and an emergency-reserve
contribution R are fixed cash amounts; a separate savings commitment equals a share s of
total income I.  All four commitments are met when

    I >= E + D + R + s * I   <=>   I >= (E + D + R) / (1 - s)

so the exact minimum threshold is (E + D + R) / (1 - s).

Checkpoint cash_needs_checkpoint = E + D + R (the combined fixed cash commitments known
before solving for income; the savings piece depends on income, so it is not yet a cash
amount at that point).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, grab

TEMPLATE_ID = "h114"


def _savings_share(text: str) -> Fraction:
    """Share of total income committed to savings, as a plain ratio."""
    m = re.search(
        rf"sav(?:e|es|ing)\s+({NUMBER})\s*(percent|%)?\s*(?:of\s+)?(?:its\s+|the\s+|their\s+)?total income",
        text,
        flags=re.S | re.I,
    )
    if m is None:
        m = re.search(rf"({NUMBER})\s*(percent|%)?\s*of\s+(?:its\s+|the\s+|their\s+)?total income", text, flags=re.S | re.I)
    if m is None:
        raise ValueError("savings share not found")
    value = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        value /= 100
    return value


def solve(text: str, q: dict) -> dict:
    essential = grab(r"essential outlays of\s+(?:USD\s+)?{N}", text)
    discretionary = grab(r"discretionary outlays of\s+(?:USD\s+)?{N}", text)
    reserve = grab(r"emergency[- ]reserve contribution of\s+(?:USD\s+)?{N}", text)
    share = _savings_share(text)

    cash_needs = essential + discretionary + reserve
    if share >= 1:
        raise ValueError("savings share of at least 100% of income: no finite threshold")
    threshold = cash_needs / (1 - share)

    return {"final": threshold, "slots": {"cash_needs_checkpoint": cash_needs}}
