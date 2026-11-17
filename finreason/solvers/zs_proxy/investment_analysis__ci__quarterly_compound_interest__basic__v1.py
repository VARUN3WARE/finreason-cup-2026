from fractions import Fraction
from finreason.nums import grab, real_pow

TEMPLATE_ID = "fp.investment_analysis.ci.quarterly_compound_interest.basic.v1"


def _pow(base: Fraction, e: Fraction) -> Fraction:
    e = Fraction(e)
    return base ** int(e) if e.denominator == 1 else real_pow(base, e)


def solve(text: str, q: dict) -> dict:
    p = grab(r"starts with USD {N}", text)
    r = grab(r"nominal annual rate of {N} percent", text)
    n = grab(r"for {N} years?", text)
    try:
        m = grab(r"m = {N}", text)
    except ValueError:
        m = Fraction(4)
    qr = r / 100 / m
    a = p * _pow(1 + qr, m * n)
    return {"final": a - p, "slots": {"quarterly_rate_trace": qr, "ending_balance_trace": a}}
