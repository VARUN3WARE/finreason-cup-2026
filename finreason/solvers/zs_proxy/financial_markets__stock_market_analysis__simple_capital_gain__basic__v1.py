from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.stock_market_analysis.simple_capital_gain.basic.v1"


def solve(text: str, q: dict) -> dict:
    n = grab(r"buys\s+{N}\s+shares", text)
    buy = grab(r"buys\s+[-\d.,/]+\s+shares at USD\s*{N}", text)
    sell = grab(r"sells them at USD\s*{N}", text)
    cost = n * buy
    proceeds = n * sell
    return {
        "final": proceeds - cost,
        "slots": {"purchase_cost_trace": cost, "sale_proceeds_trace": proceeds},
    }
