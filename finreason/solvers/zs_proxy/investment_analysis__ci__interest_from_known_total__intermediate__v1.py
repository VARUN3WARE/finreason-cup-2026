from fractions import Fraction
from finreason.nums import grab, real_pow

TEMPLATE_ID = "fp.investment_analysis.ci.interest_from_known_total.intermediate.v1"


def _pow(base: Fraction, e: Fraction) -> Fraction:
    e = Fraction(e)
    return base ** int(e) if e.denominator == 1 else real_pow(base, e)


def solve(text: str, q: dict) -> dict:
    a = grab(r"will total USD {N}", text)
    n = grab(r"after {N} years?", text)
    r = grab(r"annual rate of {N} percent", text)
    mult = _pow(1 + r / 100, n)
    p = a / mult
    return {"final": a - p, "slots": {"growth_multiplier_trace": mult, "implied_principal_trace": p}}
