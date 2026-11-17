"""h039 -- minimum equity injection to bring debt-to-equity down to a ceiling
after planned borrowing and a debt repayment (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h039"


def solve(text: str, q: dict) -> dict:
    # "A company has current debt of D and current equity of E."
    debt_now = grab(r"current debt of {N}", text)
    equity_now = grab(r"current equity of {N}", text)

    # "It plans additional borrowing of B and a debt repayment of R."
    borrowing = grab(r"additional borrowing of {N}", text)
    repayment = grab(r"debt repayment of {N}", text)

    # "... so that the debt-to-equity ratio equals the permitted ceiling C."
    ceiling = grab(r"permitted ceiling {N}", text)

    # Checkpoint: debt immediately after the planned borrowing, before repayment.
    debt_after_borrowing = debt_now + borrowing

    # Debt after both debt actions.
    debt_after_both = debt_after_borrowing - repayment

    # Ratio equation: debt_after_both / (equity_now + X) = ceiling
    #   => X = debt_after_both / ceiling - equity_now
    injection = debt_after_both / ceiling - equity_now

    # "minimum new equity injection required": an injection cannot be negative;
    # if the ceiling is already met no injection is required.
    if injection < 0:
        injection = Fraction(0)

    return {
        "final": injection,
        "slots": {"debt_after_borrowing_checkpoint": debt_after_borrowing},
    }
