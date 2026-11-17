from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.capital_structure.debt_to_equity_bond_repay_buyback.advanced.v1"


def solve(text: str, q: dict) -> dict:
    debt = grab(r"Original debt is {N}", text)
    equity = grab(r"original equity is {N}", text)
    bond = grab(r"new bond principal is {N}", text)
    repay = grab(r"scheduled debt repayment is {N}", text)
    buyback = grab(r"buyback cash is {N}", text)
    debt_after_bond = debt + bond
    adj_debt = debt_after_bond - repay
    adj_equity = equity - buyback
    return {"final": adj_debt / adj_equity, "slots": {"trace_1": debt_after_bond, "trace_2": adj_debt}}
