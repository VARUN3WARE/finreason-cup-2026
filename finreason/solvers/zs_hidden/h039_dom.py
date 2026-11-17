# FINANCE MODEL (h039)
#
# Quantity: minimum new equity injection X (USD million) that brings the leverage
# ratio (debt / equity) to the permitted ceiling c after two debt actions.
#
#   D0 = current debt, E0 = current equity (book values, USD million)
#   B  = planned additional borrowing  (increases debt)
#   R  = planned debt repayment        (decreases debt)
#
# Sequence of events (as worded: "after both debt actions"):
#   debt after borrowing, before repayment : D1 = D0 + B      <- checkpoint 1
#   debt after both actions                : D2 = D1 - R
#   equity after injection X               : E1 = E0 + X
#
# Conventions / assumptions (standard, no overrides in the text):
#   * Borrowing and repayment affect debt only; they do not change book equity
#     (cash raised/used is assumed to be an asset-side item, not equity).
#   * The injection adds one-for-one to equity and does not itself change debt
#     (cash held is not netted against debt; ratio is gross debt / equity).
#   * Ratio equation at full precision:  D2 / (E0 + X) = c
#         =>  X = D2 / c - E0
#   * "Minimum injection required": an injection cannot be negative, so if the
#     post-action ratio is already below the ceiling (D2 / E0 < c) the needed
#     injection is floored at zero.  (All 3 instances are positive; floor is
#     only a guard.)
#   * No intermediate rounding: values returned unrounded; framework rounds
#     the final answer and the checkpoint half-up to 2 dp (USD million).

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h039"


def solve(text: str, q: dict) -> dict:
    d0 = grab(r"current debt of {N}", text)
    e0 = grab(r"current equity of {N}", text)
    borrow = grab(r"additional borrowing of {N}", text)
    repay = grab(r"debt repayment of {N}", text)
    ceiling = grab(r"permitted ceiling {N}", text)

    debt_after_borrowing = d0 + borrow
    debt_after_both = debt_after_borrowing - repay

    # Equity needed so that debt / equity == ceiling
    required_equity = debt_after_both / ceiling
    injection = required_equity - e0
    if injection < 0:
        injection = Fraction(0)

    return {
        "final": injection,
        "slots": {"debt_after_borrowing_checkpoint": debt_after_borrowing},
    }
