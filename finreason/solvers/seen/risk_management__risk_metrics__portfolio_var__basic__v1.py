from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_metrics.portfolio_var.basic.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"\bV\s*=\s*{N}\s*USD", text)
    s = grab(r"volatility is s\s*=\s*{N}\s*percent", text)
    z = grab(r"multiplier is z\s*=\s*{N}", text)
    ratio = s / 100
    var = v * ratio * z  # VaR = V*(s/100)*z with z taken as given
    return {"final": Fraction(var), "slots": {"volatility_ratio_trace": ratio}}
