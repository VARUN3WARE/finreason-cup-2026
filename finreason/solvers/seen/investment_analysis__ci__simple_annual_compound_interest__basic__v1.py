from fractions import Fraction

from finreason.nums import grab, real_pow

TEMPLATE_ID = "fp.investment_analysis.ci.simple_annual_compound_interest.basic.v1"


def _pow(base: Fraction, n: Fraction) -> Fraction:
    if n.denominator == 1:
        return base ** int(n)
    return real_pow(base, n)


def solve(text: str, q: dict) -> dict:
    principal = grab(r"starts with\s+USD\s+{N}", text)
    rate = grab(r"annual rate of\s+{N}\s+percent", text) / 100
    years = grab(r"compounds annually for\s+{N}\s+years?", text)
    mult = _pow(1 + rate, years)
    ending = principal * mult
    return {
        "final": ending - principal,
        "slots": {
            "ending_balance_trace": ending,
            "growth_multiplier_trace": mult,
        },
    }
