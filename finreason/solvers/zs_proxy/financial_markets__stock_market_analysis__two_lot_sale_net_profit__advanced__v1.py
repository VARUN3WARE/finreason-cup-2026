from fractions import Fraction
from finreason.nums import grab_all

TEMPLATE_ID = "fp.financial_markets.stock_market_analysis.two_lot_sale_net_profit.advanced.v1"


def solve(text: str, q: dict) -> dict:
    n1, p1 = grab_all(r"buys\s+{N}\s+shares at USD\s*{N}", text)
    n2, p2 = grab_all(r"and\s+{N}\s+more shares at USD\s*{N}", text)
    (sell,) = grab_all(r"sells all shares at USD\s*{N}", text)
    total_shares = n1 + n2
    total_cost = n1 * p1 + n2 * p2
    avg = total_cost / total_shares
    proceeds = total_shares * sell
    return {
        "final": proceeds - total_cost,
        "slots": {
            "total_shares_trace": total_shares,
            "average_cost_trace": avg,
            "sale_proceeds_trace": proceeds,
        },
    }
