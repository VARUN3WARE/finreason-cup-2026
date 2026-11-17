"""h063 -- household budget cut: reduce flexible spending vs outside funding.

Literal transcription of the question, sentence by sentence.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h063"


def _cut_rate(text: str) -> Fraction:
    # "A cut of 0.2 is imposed" -> fractional cut of the total budget.
    m = re.search(r"cut of (" + NUMBER + r")\s*(percent|%)?", text)
    if m is None:
        raise ValueError("cut not found")
    val = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        val = val / 100
    return val


def solve(text: str, q: dict) -> dict:
    # S1: "A household starts with a total budget of B."
    total_budget = grab(r"total budget of (?:USD\s*)?\$?{N}", text)

    # S2: "A cut of c is imposed while protected spending of P and planned
    #      flexible spending of X are intended to continue."
    cut = _cut_rate(text)
    protected = grab(r"protected spending of (?:USD\s*)?\$?{N}", text)
    planned_flexible = grab(r"planned flexible spending of (?:USD\s*)?\$?{N}", text)

    # Budget remaining after the cut (checkpoint 1).
    post_cut_budget = total_budget * (1 - cut)

    # Funding gap: intended spending (protected + planned flexible) minus the
    # budget remaining after the cut.
    intended_spending = protected + planned_flexible
    funding_gap = intended_spending - post_cut_budget

    # S3: "Flexible spending may not fall below F, and at most O of outside
    #      funding is available."
    flexible_floor = grab(r"may not fall below (?:USD\s*)?\$?{N}", text)
    outside_available = grab(r"at most (?:USD\s*)?\$?{N} of outside funding", text)

    # Flexible spending available for reduction (checkpoint 2): planned
    # flexible spending above its floor (cannot be negative).
    reducible = planned_flexible - flexible_floor
    if reducible < 0:
        reducible = Fraction(0)

    # S4: "Prefer reducing flexible spending if that alone covers the funding
    #      gap; otherwise use outside funding if it alone covers the gap."
    if reducible >= funding_gap:
        final = "reduce_flexible_spending"
    elif outside_available >= funding_gap:
        final = "use_external_funding"
    else:
        final = "no_feasible_response"

    return {
        "final": final,
        "slots": {
            "post_cut_budget_checkpoint": post_cut_budget,
            "reducible_spending_checkpoint": reducible,
        },
    }
