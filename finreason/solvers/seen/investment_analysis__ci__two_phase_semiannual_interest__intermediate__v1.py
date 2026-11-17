from fractions import Fraction
import re

from finreason.nums import grab, real_pow

TEMPLATE_ID = "fp.investment_analysis.ci.two_phase_semiannual_interest.intermediate.v1"

_FREQ = {
    "annually": 1,
    "semiannually": 2,
    "semi-annually": 2,
    "quarterly": 4,
    "monthly": 12,
}


def _pow(base: Fraction, n: Fraction) -> Fraction:
    if n.denominator == 1:
        return base ** int(n)
    return real_pow(base, n)


def solve(text: str, q: dict) -> dict:
    principal = grab(r"USD\s+{N}\s+is compounded", text)
    fm = re.search(r"is compounded\s+([A-Za-z-]+)", text)
    m = Fraction(_FREQ.get(fm.group(1).lower(), 2)) if fm else Fraction(2)
    n1, r1 = (
        grab(r"first\s+{N}\s+years?", text),
        grab(r"first\s+{N}\s+years?\s+the nominal annual rate is\s+{N}\s+percent", text, 2) / 100,
    )
    n2, r2 = (
        grab(r"next\s+{N}\s+years?", text),
        grab(r"next\s+{N}\s+years?\s+it is\s+{N}\s+percent", text, 2) / 100,
    )
    g1 = _pow(1 + r1 / m, m * n1)
    g2 = _pow(1 + r2 / m, m * n2)
    ending = principal * g1 * g2
    return {
        "final": ending - principal,
        "slots": {
            "first_growth_trace": g1,
            "second_growth_trace": g2,
            "ending_balance_trace": ending,
        },
    }
