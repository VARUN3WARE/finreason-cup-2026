from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.levratio.debt_repayment_and_borrowing.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    liabilities = grab(r"Opening total liabilities are {N}", text)
    equity = grab(r"equity is {N}", text)
    repay = grab(r"repays {N}", text)
    new = grab(r"incurs {N}", text)
    after_repay = liabilities - repay
    closing = after_repay + new
    return {
        "final": closing / equity,
        "slots": {"trace_1": after_repay, "trace_2": closing},
    }
