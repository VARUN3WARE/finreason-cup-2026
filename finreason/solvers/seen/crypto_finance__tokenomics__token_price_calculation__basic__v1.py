from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.tokenomics.token_price_calculation.basic.v1"


def solve(text: str, q: dict) -> dict:
    mcap = grab(r"market capitalization of {N} USD", text)
    supply = grab(r"and {N} (?:token )?units in circulation", text)
    return {"final": mcap / supply, "slots": {}}
