"""Household budget cut: choose between trimming flexible spending, outside funding, or neither.

post-cut budget  = total budget * (1 - cut fraction)
funding gap      = protected + planned flexible - post-cut budget
reducible        = planned flexible - flexible floor   (never below zero)
decision         : reducible >= gap -> reduce_flexible_spending
                   elif outside cap >= gap -> use_external_funding
                   else no_feasible_response
"""

from fractions import Fraction
import re

from finreason.nums import grab, F, NUMBER

TEMPLATE_ID = "h063"


def _cut_fraction(text: str, budget: Fraction) -> Fraction:
    m = re.search(r"cut of (" + NUMBER + r")\s*(percent|%)?", text)
    if m is None:
        raise ValueError("cut not found")
    v = F(m.group(1))
    if m.group(2):
        return v / 100
    if v <= 1:
        return v
    # absolute amount cut stated in currency
    return v / budget


def solve(text: str, q: dict) -> dict:
    budget = grab(r"total budget of (?:USD |\$)?{N}", text)
    cut = _cut_fraction(text, budget)
    protected = grab(r"protected spending of (?:USD |\$)?{N}", text)
    flexible = grab(r"planned flexible spending of (?:USD |\$)?{N}", text)
    floor = grab(r"may not fall below (?:USD |\$)?{N}", text)
    outside = grab(r"at most (?:USD |\$)?{N} of outside funding", text)

    post_cut = budget * (1 - cut)
    gap = protected + flexible - post_cut
    reducible = flexible - floor
    if reducible < 0:
        reducible = Fraction(0)

    if reducible >= gap:
        final = "reduce_flexible_spending"
    elif outside >= gap:
        final = "use_external_funding"
    else:
        final = "no_feasible_response"

    return {
        "final": final,
        "slots": {
            "post_cut_budget_checkpoint": post_cut,
            "reducible_spending_checkpoint": reducible,
        },
    }
