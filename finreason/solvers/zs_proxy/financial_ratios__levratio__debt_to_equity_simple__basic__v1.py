from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.levratio.debt_to_equity_simple.basic.v1"


def solve(text: str, q: dict) -> dict:
    liab = grab(r"total liabilities of {N} USD", text)
    eq = grab(r"total equity of {N} USD", text)
    return {"final": Fraction(liab) / eq, "slots": {}}
