from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.forex_trading.eur_to_gbp_cross_conversion.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    euros = grab(r"Convert {N} whole euros", text)
    usd_per_eur = grab(r"EUR/USD\s*=\s*{N}\s*USD per euro", text)
    usd_per_gbp = grab(r"GBP/USD\s*=\s*{N}\s*USD per pound", text)
    # Cross rate as stated: GBP per EUR = (USD per EUR) / (USD per GBP); no rounding.
    cross = Fraction(usd_per_eur) / usd_per_gbp
    return {"final": euros * cross, "slots": {"cross_rate_trace": cross}}
