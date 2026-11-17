from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.rar.m_squared_measure.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    # Displayed percentage values used directly (percent units).
    rp = grab(r"portfolio return is {N} percent", text)
    sp = grab(r"portfolio return is {N} percent with standard deviation {N} percent", text, group=2)
    rf = grab(r"risk-free rate is {N} percent", text)
    sm = grab(r"market standard deviation is {N} percent", text)
    excess = rp - rf
    sharpe = excess / sp
    scaled = sharpe * sm
    m2 = rf + scaled
    return {
        "final": m2,
        "slots": {
            "excess_return_trace": excess,
            "sharpe_ratio_trace": sharpe,
            "scaled_premium_trace": scaled,
        },
    }
