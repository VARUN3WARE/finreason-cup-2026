from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.investment_analysis.rar.three_asset_capm_portfolio.advanced.v1"


def solve(text: str, q: dict) -> dict:
    holdings = []
    for name in ("A", "B", "C"):
        value, beta = grab_all(r"USD {N} of asset " + name + r" with beta {N}", text)
        holdings.append((value, beta))
    rf = grab(r"risk-free rate is {N} percent", text)
    rm = grab(r"expected market return is {N} percent", text)
    total = sum((v for v, _ in holdings), Fraction(0))
    # Exact dollar weights, unrounded.
    beta_p = sum((v / total * b for v, b in holdings), Fraction(0))
    premium = rm - rf
    return {
        "final": rf + beta_p * premium,
        "slots": {
            "total_value_trace": total,
            "portfolio_beta_trace": beta_p,
            "market_premium_trace": premium,
        },
    }
