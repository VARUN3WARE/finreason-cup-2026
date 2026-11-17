from fractions import Fraction

from finreason.nums import grab, real_pow

TEMPLATE_ID = "fp.investment_analysis.ci.interest_from_known_total.intermediate.v1"


def _pow(base: Fraction, n: Fraction) -> Fraction:
    if n.denominator == 1:
        return base ** int(n)
    return real_pow(base, n)


def solve(text: str, q: dict) -> dict:
    total = grab(r"total\s+USD\s+{N}", text)
    years = grab(r"after\s+{N}\s+years?", text)
    rate = grab(r"annual rate of\s+{N}\s+percent", text) / 100
    mult = _pow(1 + rate, years)
    principal = total / mult
    return {
        "final": total - principal,
        "slots": {
            "growth_multiplier_trace": mult,
            "implied_principal_trace": principal,
        },
    }
