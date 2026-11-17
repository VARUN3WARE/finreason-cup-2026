from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.personalinvest.volatility_band.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    ev = grab(r"Expected value in USD is {N}", text)
    vol = grab(r"Volatility ratio is {N}", text)
    spread = ev * vol
    lower = ev - spread
    upper = ev + spread
    return {"final": upper, "slots": {"band_spread_usd": spread, "lower_bound_usd": lower}}
