from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.levratio.capital_injection.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    liabilities = grab(r"Total liabilities are {N}", text)
    equity = grab(r"total equity before an owner capital injection is {N}", text)
    injection = grab(r"injection adds {N}", text)
    eq_after = equity + injection
    return {"final": liabilities / eq_after, "slots": {"trace_1": eq_after}}
