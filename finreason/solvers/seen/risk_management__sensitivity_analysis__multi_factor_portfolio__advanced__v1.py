from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.sensitivity_analysis.multi_factor_portfolio.advanced.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"\bV\s*=\s*{N}", text)
    ci = grab(r"\bci\s*=\s*{N}", text)
    cm = grab(r"\bcm\s*=\s*{N}", text)
    cc = grab(r"\bcc\s*=\s*{N}", text)
    si = grab(r"\bsi\s*=\s*{N}", text)
    sm = grab(r"\bsm\s*=\s*{N}", text)
    sc = grab(r"\bsc\s*=\s*{N}", text)
    # Each effect ratio = sensitivity * change / 100; total change = V * sum of effects.
    interest = si * ci / 100
    market = sm * cm / 100
    credit = sc * cc / 100
    total = v * (interest + market + credit)
    return {
        "final": total,
        "slots": {
            "interest_effect_trace": interest,
            "market_effect_trace": market,
            "credit_effect_trace": credit,
        },
    }
