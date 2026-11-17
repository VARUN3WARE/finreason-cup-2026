from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.capital_structure.debt_to_equity_bond_repay_buyback.advanced.v1"


def solve(text: str, q: dict) -> dict:
    debt = grab(r"[Oo]riginal debt is {N} USD million", text)
    equity = grab(r"[Oo]riginal equity is {N} USD million", text)
    bond = grab(r"new bond principal is {N} USD million", text)
    repay = grab(r"scheduled debt repayment is {N} USD million", text)
    buyback = grab(r"buyback cash is {N} USD million", text)
    debt_after_bond = debt + bond
    debt_after_repay = debt_after_bond - repay
    adj_equity = equity - buyback
    return {"final": debt_after_repay / adj_equity,
            "slots": {"trace_1": debt_after_bond, "trace_2": debt_after_repay}}
