# h114 -- minimum total income that covers three fixed cash commitments plus an income-proportional
# savings commitment.
#
# ======================================================================================================
# ECONOMIC MODEL (written before coding)
# ======================================================================================================
# Symbols (all USD unless noted):
#   Y = total income                                   -- the unknown being solved for
#   E = essential outlays                              -- fixed amount  ("essential outlays of {N}")
#   D = planned discretionary outlays                  -- fixed amount  ("planned discretionary outlays of {N}")
#   R = emergency-reserve contribution                 -- fixed amount  ("emergency-reserve contribution of {N}")
#   s = savings rate (dimensionless fraction of income)-- ("saving {N} of total income"); the text gives a plain
#       fraction, so 0.2 means 20% of Y.  It is NOT a "percent"-unit number here (no /100 applied) unless the
#       text itself attaches "percent" / "%" to it (handled defensively below; not the case in the 3 instances).
#
# The four commitments are: E, D, R and the separate savings commitment S = s * Y.
# "Meets all four commitments" = total income is enough to fund every commitment simultaneously:
#
#       Y  >=  E + D + R + S          with  S = s * Y
#       Y  >=  E + D + R + s * Y
#       Y * (1 - s)  >=  E + D + R
#       Y_min = (E + D + R) / (1 - s)            <- the threshold: the income at which the inequality binds
#
# The savings commitment is itself a function of the income being solved for, so it cannot simply be added to
# the fixed outlays (that would be the classic error of computing C + s*C); it has to be solved for through the
# (1 - s) denominator.  Equivalently Y_min = C + s*Y_min.
#
# Feasibility: a finite threshold exists iff s < 1 (with s >= 1, saving alone eats all income and no income level
# works).  The text says to judge feasibility on the UNROUNDED exact threshold; here s is 0.2 / 0.2 / 0.25, so it
# is always feasible, and the reported figure is only the half-up 2-dp display of the exact rational Y_min (the
# framework does the rounding; this module returns the exact Fraction).  Nothing is rounded inside the
# computation: e.g. R = 101.683 keeps its 3rd decimal, per "exact arithmetic through all intermediate steps".
#
# Checkpoint  cash_needs_checkpoint  ("the combined cash commitments before solving for income", position 1, usd):
#       C = E + D + R
# i.e. the sum of the three FIXED-dollar commitments.  The savings commitment s*Y is excluded because, before
# the income is solved for, it is not a cash amount at all (it is a fraction of the unknown).  The final answer
# is then C / (1 - s).
#
# Conventions: no overrides of standard finance conventions in the text; "fictional household" -> only the stated
# rules apply (no taxes, no interest, no timing effects).
# ======================================================================================================

import re
from fractions import Fraction

from finreason.nums import NUMBER, grab, F

TEMPLATE_ID = "h114"


def _savings_rate(text: str) -> Fraction:
    """Savings commitment as a fraction of total income ('saving 0.2 of total income')."""
    m = re.search(
        r"saving\s+(" + NUMBER + r")\s*(%|percent|per cent)?\s+of\s+(?:its\s+|their\s+|the\s+|his\s+|her\s+)?total income",
        text,
        flags=re.S | re.I,
    )
    if m is None:
        raise ValueError("savings-rate phrase not found")
    s = F(m.group(1))
    if m.group(2):  # explicitly stated as a percent -> convert to a plain fraction
        s = s / 100
    return s


def solve(text: str, q: dict) -> dict:
    essential = grab(r"essential outlays of {N}", text)
    discretionary = grab(r"planned discretionary outlays of {N}", text)
    reserve = grab(r"emergency-reserve contribution of {N}", text)
    s = _savings_rate(text)

    # Checkpoint: fixed-dollar commitments only (savings share is income-dependent, so not yet a cash amount).
    cash_needs = essential + discretionary + reserve

    # Feasibility on the exact (unrounded) rational: a finite income threshold exists iff s < 1.
    if s >= 1:
        raise ValueError("infeasible: savings share absorbs all income (s >= 1)")

    # Y >= C + s*Y  =>  Y_min = C / (1 - s)
    income_threshold = cash_needs / (1 - s)

    return {
        "final": income_threshold,
        "slots": {"cash_needs_checkpoint": cash_needs},
    }
