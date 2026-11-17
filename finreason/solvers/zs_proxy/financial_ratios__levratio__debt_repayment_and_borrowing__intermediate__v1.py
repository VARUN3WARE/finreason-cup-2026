from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.levratio.debt_repayment_and_borrowing.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    liab0 = grab(r"[Oo]pening total liabilities are {N} USD", text)
    eq = grab(r"equity is {N} USD", text)
    repay = grab(r"repays {N} USD of liabilities", text)
    new = grab(r"incurs {N} USD of new liabilities", text)
    after_repay = liab0 - repay
    closing = after_repay + new
    return {"final": Fraction(closing) / eq, "slots": {"trace_1": after_repay, "trace_2": closing}}
