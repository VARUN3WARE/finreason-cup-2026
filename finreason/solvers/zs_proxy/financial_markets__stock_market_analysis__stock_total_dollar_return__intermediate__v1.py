from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.stock_market_analysis.stock_total_dollar_return.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    n = grab(r"buys\s+{N}\s+shares", text)
    buy = grab(r"buys\s+[-\d.,/]+\s+shares at USD\s*{N}", text)
    dps = grab(r"dividend of USD\s*{N}\s+per share", text)
    sell = grab(r"sells all shares at USD\s*{N}", text)
    cost = n * buy
    divs = n * dps
    proceeds = n * sell
    return {
        "final": proceeds + divs - cost,
        "slots": {
            "purchase_cost_trace": cost,
            "total_dividends_trace": divs,
            "sale_proceeds_trace": proceeds,
        },
    }
