from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.capital_structure.debt_to_equity_after_buyback.basic.v1"


def solve(text: str, q: dict) -> dict:
    debt = grab(r"Total debt is {N}", text)
    equity = grab(r"equity before the buyback is {N}", text)
    buyback = grab(r"buyback cash is {N}", text)
    adj_equity = equity - buyback
    return {"final": debt / adj_equity, "slots": {"trace_1": adj_equity}}
