from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.levratio.convertible_debt.basic.v1"


def solve(text: str, q: dict) -> dict:
    liab0 = grab(r"total liabilities are {N} USD", text)
    eq0 = grab(r"and equity is {N} USD", text)
    conv = grab(r"Convertible debt of {N} USD", text)
    liab1 = liab0 - conv
    eq1 = eq0 + conv
    return {"final": Fraction(liab1) / eq1, "slots": {"trace_1": liab1, "trace_2": eq1}}
