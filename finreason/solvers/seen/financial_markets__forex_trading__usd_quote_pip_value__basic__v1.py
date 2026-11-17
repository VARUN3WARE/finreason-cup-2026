from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.forex_trading.usd_quote_pip_value.basic.v1"


def solve(text: str, q: dict) -> dict:
    units = grab(r"contains {N} base-currency units", text)
    pip = grab(r"One pip changes the USD quote by USD {N} per base unit", text)
    return {"final": Fraction(units) * pip, "slots": {}}
