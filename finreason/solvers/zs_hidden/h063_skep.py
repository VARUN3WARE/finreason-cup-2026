"""h063 -- household budget cut: reduce flexible spending vs. outside funding vs. no feasible response.

AMBIGUITY HUNT (resolutions with textual evidence)
--------------------------------------------------
A1. "A cut of 0.2 is imposed" -- fraction of the budget, or an absolute amount?
    Values are 0.2 / 0.25 on budgets of ~1000-1300: an absolute cut of 0.2 would be
    meaningless.  Checkpoint 1 is "the budget remaining after the cut", so the cut is a
    proportional cut applied to the TOTAL budget:  post_cut = B * (1 - c).
    (If a variant phrases it as "20 percent"/"20%", the solver divides by 100.)

A2. What is "the funding gap"?  Two candidate readings:
      (i)  gap = cut amount = B * c                       (ignores P and F entirely)
      (ii) gap = (protected + planned flexible) - post_cut_budget
    The text says the cut is imposed "while protected spending of P and planned flexible
    spending of F are intended to continue": the gap is what is missing to keep funding
    the intended spending out of the reduced budget, i.e. reading (ii).  Reading (i)
    would make the position-1 checkpoint (post-cut budget) irrelevant to the chain and
    would silently assume B == P + F, which is false in every instance (1122 vs 1016,
    1423 vs 1284.13, 1201 vs 1235).  Resolved: gap = P + F - B*(1 - c).
    Note the two readings give DIFFERENT enum answers on two of the three instances, so
    this is the load-bearing decision.

A3. Protected spending is never cut ("protected ... intended to continue"); the cut
    hits the budget, not the spending lines.

A4. "Flexible spending may not fall below Fmin" -> the amount available for reduction is
    F - Fmin (checkpoint 2, "flexible spending available for reduction").  It is the
    AVAILABLE amount, not min(available, gap).  Floored at zero (an "available" amount
    cannot be negative); the floor is inactive on all three instances.

A5. "covers the funding gap": non-strict -- an amount exactly equal to the gap covers it
    (reducible >= gap; outside >= gap).  "at most X of outside funding is available"
    -> outside funding covers the gap iff X >= gap.

A6. Combination of the two responses is NOT an option: each rule says "if that ALONE
    covers"; otherwise the stated fallback is no_feasible_response.

A7. Priority/tie-break: "Prefer reducing flexible spending if that alone covers";
    "otherwise use outside funding if it alone covers"; else no feasible response.
    Strict ordering, evaluated exactly in that sequence.

A8. gap <= 0 (budget after cut already funds intended spending): nothing needs covering,
    so reducing flexible spending by zero trivially "covers" it -> reduce_flexible_spending.
    Not triggered on any instance (gaps are 309.2, 395.695, 274.75).

A9. Rounding: checkpoints are rendered half-up to 2dp by the framework.  All comparisons
    use EXACT Fractions (never the displayed checkpoints).  Instance 2's post-cut budget is
    exactly 1027.305, a deliberate half-up test (-> 1027.31).

A10. Units: all amounts are plain USD; no scaling.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, F, NUMBER

TEMPLATE_ID = "h063"

REDUCE = "reduce_flexible_spending"
EXTERNAL = "use_external_funding"
NONE = "no_feasible_response"


def _cut_fraction(text: str) -> Fraction:
    """Cut as a fraction of the total budget (handles '0.2', '20 percent', '20%')."""
    m = re.search(rf"cut of ({NUMBER})\s*(percent|%)?", text, flags=re.S)
    if m is None:
        raise ValueError("cut not found")
    c = F(m.group(1))
    if m.group(2):
        c = c / 100
    return c


def solve(text: str, q: dict) -> dict:
    budget = grab(r"total budget of {N}", text)
    cut = _cut_fraction(text)
    protected = grab(r"protected spending of {N}", text)
    flexible = grab(r"planned flexible spending of {N}", text)
    flex_floor = grab(r"may not fall below {N}", text)
    outside_max = grab(r"at most {N} of outside funding", text)

    # Position 1: budget remaining after the proportional cut (A1).
    post_cut_budget = budget * (1 - cut)

    # Funding gap: intended spending that the reduced budget no longer covers (A2, A3).
    gap = protected + flexible - post_cut_budget

    # Position 2: flexible spending available for reduction, floored at zero (A4).
    reducible = max(Fraction(0), flexible - flex_floor)

    # Decision rules in the stated priority order (A5-A8).
    if reducible >= gap:
        final = REDUCE
    elif outside_max >= gap:
        final = EXTERNAL
    else:
        final = NONE

    return {
        "final": final,
        "slots": {
            "post_cut_budget_checkpoint": post_cut_budget,
            "reducible_spending_checkpoint": reducible,
        },
    }
