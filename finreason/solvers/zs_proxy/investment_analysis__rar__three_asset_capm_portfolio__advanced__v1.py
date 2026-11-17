import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "fp.investment_analysis.rar.three_asset_capm_portfolio.advanced.v1"

_HOLDING = re.compile(rf"USD ({NUMBER}) of asset (\w+) with beta ({NUMBER})")


def solve(text: str, q: dict) -> dict:
    holdings = [(F(v), F(b)) for v, _name, b in _HOLDING.findall(text)]
    if len(holdings) < 2:
        raise ValueError("could not parse holdings")
    total = sum((v for v, _ in holdings), Fraction(0))
    beta_p = sum((v * b for v, b in holdings), Fraction(0)) / total
    rf = grab(r"risk-free rate is {N} percent", text)
    rm = grab(r"expected market return is {N} percent", text)
    premium = rm - rf
    capm = rf + beta_p * premium
    return {
        "final": capm,
        "slots": {
            "total_value_trace": total,
            "portfolio_beta_trace": beta_p,
            "market_premium_trace": premium,
        },
    }
