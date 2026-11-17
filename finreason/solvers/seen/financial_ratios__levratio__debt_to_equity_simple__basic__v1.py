from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.levratio.debt_to_equity_simple.basic.v1"


def solve(text: str, q: dict) -> dict:
    liabilities = grab(r"total liabilities of {N}", text)
    equity = grab(r"total equity of {N}", text)
    return {"final": liabilities / equity, "slots": {}}
