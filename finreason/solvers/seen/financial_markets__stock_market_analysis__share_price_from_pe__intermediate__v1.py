from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.stock_market_analysis.share_price_from_pe.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    pe = grab(r"P/E multiple of {N}", text)
    earnings = grab(r"total earnings of (?:USD\s*)?{N}", text)
    shares = grab(r"{N} shares outstanding", text)
    eps = Fraction(earnings) / shares
    return {"final": pe * eps, "slots": {"earnings_per_share_trace": eps}}
