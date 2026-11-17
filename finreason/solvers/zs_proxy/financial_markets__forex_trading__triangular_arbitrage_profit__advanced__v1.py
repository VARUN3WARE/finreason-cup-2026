from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.forex_trading.triangular_arbitrage_profit.advanced.v1"


def solve(text: str, q: dict) -> dict:
    start = grab(r"Start with USD {N}", text)
    a_per_usd = grab(r"{N} units? of currency A per USD", text)
    b_per_a = grab(r"{N} units? of currency B per unit of A", text)
    usd_per_b = grab(r"USD {N} per unit of B", text)
    a = start * a_per_usd
    b = a * b_per_a
    end = b * usd_per_b
    return {
        "final": end - start,
        "slots": {"foreign_a_trace": a, "foreign_b_trace": b, "ending_usd_trace": end},
    }
