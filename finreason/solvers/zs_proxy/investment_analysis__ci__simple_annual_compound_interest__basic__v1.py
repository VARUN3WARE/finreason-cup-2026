from fractions import Fraction
from finreason.nums import grab, real_pow

TEMPLATE_ID = "fp.investment_analysis.ci.simple_annual_compound_interest.basic.v1"


def _pow(base: Fraction, e: Fraction) -> Fraction:
    e = Fraction(e)
    return base ** int(e) if e.denominator == 1 else real_pow(base, e)


def solve(text: str, q: dict) -> dict:
    p = grab(r"starts with USD {N}", text)
    r = grab(r"nominal annual rate of {N} percent", text)
    n = grab(r"compounds annually for {N} years?", text)
    mult = _pow(1 + r / 100, n)
    a = p * mult
    return {"final": a - p, "slots": {"ending_balance_trace": a, "growth_multiplier_trace": mult}}
