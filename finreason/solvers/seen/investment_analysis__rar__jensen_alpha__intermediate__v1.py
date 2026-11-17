from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.rar.jensen_alpha.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    # All values are displayed percentages; work in percentage points directly.
    rp = grab(r"portfolio returned {N} percent", text)
    rf = grab(r"risk-free rate was {N} percent", text)
    rm = grab(r"market returned {N} percent", text)
    beta = grab(r"portfolio beta was {N}", text)
    premium = rm - rf
    capm = rf + beta * premium
    return {
        "final": rp - capm,
        "slots": {"market_premium_trace": premium, "capm_return_trace": capm},
    }
