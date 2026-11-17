from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.stock_market_analysis.dividend_yield.basic.v1"


def solve(text: str, q: dict) -> dict:
    div = grab(r"annual dividend of USD\s*{N}", text)
    price = grab(r"trades at USD\s*{N}", text)
    ratio = div / price
    return {"final": ratio * 100, "slots": {"yield_ratio_trace": ratio}}
