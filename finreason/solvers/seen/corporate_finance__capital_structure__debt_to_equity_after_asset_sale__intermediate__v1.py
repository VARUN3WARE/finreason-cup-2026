from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.capital_structure.debt_to_equity_after_asset_sale.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    debt = grab(r"Original debt is {N}", text)
    equity = grab(r"equity is {N}", text)
    price = grab(r"asset sale price is {N}", text)
    cost = grab(r"transaction cost is {N}", text)
    net = price - cost
    adj_debt = max(Fraction(0), debt - net)
    return {"final": adj_debt / equity, "slots": {"trace_1": net, "trace_2": adj_debt}}
