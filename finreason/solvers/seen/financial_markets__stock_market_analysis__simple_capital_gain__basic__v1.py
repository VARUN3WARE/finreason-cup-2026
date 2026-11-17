from fractions import Fraction

from finreason.nums import grab_all

TEMPLATE_ID = "fp.financial_markets.stock_market_analysis.simple_capital_gain.basic.v1"


def solve(text: str, q: dict) -> dict:
    n, buy = grab_all(r"buys {N} shares at (?:USD\s*)?{N} per share", text)
    sell = grab_all(r"sells them at (?:USD\s*)?{N} per share", text)[0]
    cost = n * buy
    proceeds = n * sell
    return {
        "final": proceeds - cost,
        "slots": {"purchase_cost_trace": cost, "sale_proceeds_trace": proceeds},
    }
