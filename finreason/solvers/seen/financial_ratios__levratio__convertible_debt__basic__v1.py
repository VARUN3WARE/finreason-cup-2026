from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.levratio.convertible_debt.basic.v1"


def solve(text: str, q: dict) -> dict:
    liabilities = grab(r"total liabilities are {N}", text)
    equity = grab(r"equity is {N}", text)
    conv = grab(r"Convertible debt of {N}", text)
    liab_after = liabilities - conv
    eq_after = equity + conv
    return {
        "final": liab_after / eq_after,
        "slots": {"trace_1": liab_after, "trace_2": eq_after},
    }
