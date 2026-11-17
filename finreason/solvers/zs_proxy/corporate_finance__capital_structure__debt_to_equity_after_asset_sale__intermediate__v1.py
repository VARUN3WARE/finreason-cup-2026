from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.capital_structure.debt_to_equity_after_asset_sale.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    debt = grab(r"[Oo]riginal debt is {N} USD million", text)
    equity = grab(r"[Ee]quity is {N} USD million", text)
    sale = grab(r"asset sale price is {N} USD million", text)
    cost = grab(r"transaction cost is {N} USD million", text)
    net = sale - cost                      # net proceeds = sale price - transaction cost
    adj_debt = debt - net                  # all net proceeds repay debt
    if adj_debt < 0:                       # floored at zero
        adj_debt = Fraction(0)
    return {"final": adj_debt / equity, "slots": {"trace_1": net, "trace_2": adj_debt}}
