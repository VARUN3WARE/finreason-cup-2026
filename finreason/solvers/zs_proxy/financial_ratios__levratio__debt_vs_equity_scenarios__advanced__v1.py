from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.levratio.debt_vs_equity_scenarios.advanced.v1"


def solve(text: str, q: dict) -> dict:
    liab = grab(r"[Cc]urrent liabilities are {N} USD", text)
    eq = grab(r"current equity is {N} USD", text)
    new_debt = grab(r"issues {N} USD of debt", text)
    new_eq = grab(r"issues {N} USD of equity", text)
    de_debt = Fraction(liab + new_debt) / eq
    de_eq = Fraction(liab) / (eq + new_eq)
    return {"final": de_debt - de_eq, "slots": {"trace_1": de_debt, "trace_2": de_eq}}
