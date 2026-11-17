from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.financial_markets.stock_market_analysis.stock_total_dollar_return.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    n, buy = grab_all(r"buys {N} shares at (?:USD\s*)?{N} each", text)
    dps = grab(r"dividend of (?:USD\s*)?{N} per share", text)
    sell = grab(r"sells all shares at (?:USD\s*)?{N} each", text)
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
