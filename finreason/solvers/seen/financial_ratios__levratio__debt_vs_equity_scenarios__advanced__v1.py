from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.levratio.debt_vs_equity_scenarios.advanced.v1"


def solve(text: str, q: dict) -> dict:
    liabilities = grab(r"Current liabilities are {N}", text)
    equity = grab(r"current equity is {N}", text)
    new_debt = grab(r"issues {N} USD of debt", text)
    new_equity = grab(r"issues {N} USD of equity", text)
    de_debt = (liabilities + new_debt) / equity
    de_equity = liabilities / (equity + new_equity)
    return {
        "final": de_debt - de_equity,
        "slots": {"trace_1": de_debt, "trace_2": de_equity},
    }
