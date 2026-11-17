from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.capital_structure.debt_to_equity_aggregate_debt.basic.v1"


def solve(text: str, q: dict) -> dict:
    st = grab(r"Short-term debt is {N}", text)
    lt = grab(r"long-term debt is {N}", text)
    equity = grab(r"shareholders' equity is {N}", text)
    total = st + lt
    return {"final": total / equity, "slots": {"trace_1": total}}
