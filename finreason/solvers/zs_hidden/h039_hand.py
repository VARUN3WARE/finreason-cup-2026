from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h039"


def solve(text: str, q: dict) -> dict:
    debt = grab(r"current debt of {N}", text)
    equity = grab(r"current equity of {N}", text)
    borrow = grab(r"additional borrowing of {N}", text)
    repay = grab(r"debt repayment of {N}", text)
    ceiling = grab(r"permitted ceiling {N}", text)

    debt_after_borrow = debt + borrow
    debt_final = debt_after_borrow - repay
    # (E + x) * ceiling = D_final  ->  x = D_final / ceiling - E ; minimum injection cannot be negative
    injection = debt_final / ceiling - equity
    if injection < 0:
        injection = Fraction(0)
    return {"final": injection,
            "slots": {"debt_after_borrowing_checkpoint": debt_after_borrow}}
