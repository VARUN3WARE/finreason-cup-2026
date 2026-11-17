from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.sensitivity_analysis.multi_factor_portfolio.advanced.v1"


def solve(text: str, q: dict) -> dict:
    V = grab(r"\bV\s*=\s*{N}", text)
    ci = grab(r"\bci\s*=\s*{N}", text)
    cm = grab(r"\bcm\s*=\s*{N}", text)
    cc = grab(r"\bcc\s*=\s*{N}", text)
    si = grab(r"\bsi\s*=\s*{N}", text)
    sm = grab(r"\bsm\s*=\s*{N}", text)
    sc = grab(r"\bsc\s*=\s*{N}", text)
    ie = si * ci / 100
    me = sm * cm / 100
    ce = sc * cc / 100
    total = V * (ie + me + ce)
    return {
        "final": total,
        "slots": {"interest_effect_trace": ie, "market_effect_trace": me, "credit_effect_trace": ce},
    }
