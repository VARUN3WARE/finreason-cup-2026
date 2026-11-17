from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.capital_structure.debt_to_equity_bond_and_buyback.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    debt = grab(r"Existing debt is {N}", text)
    equity = grab(r"original equity is {N}", text)
    bond = grab(r"new bond issue is {N}", text)
    buyback = grab(r"buyback cash is {N}", text)
    adj_debt = debt + bond
    adj_equity = equity - buyback
    return {"final": adj_debt / adj_equity, "slots": {"trace_1": adj_debt, "trace_2": adj_equity}}
