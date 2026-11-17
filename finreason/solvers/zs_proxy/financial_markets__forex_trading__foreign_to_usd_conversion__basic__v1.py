from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.forex_trading.foreign_to_usd_conversion.basic.v1"


def solve(text: str, q: dict) -> dict:
    amount = grab(r"Convert {N} units of a foreign", text)
    quote = grab(r"direct quote of USD {N} per foreign unit", text)
    return {"final": amount * quote, "slots": {}}
