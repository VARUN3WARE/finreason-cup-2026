from fractions import Fraction
from finreason.nums import grab, real_pow

TEMPLATE_ID = "fp.investment_analysis.ci.two_phase_semiannual_interest.intermediate.v1"


def _pow(base: Fraction, e: Fraction) -> Fraction:
    e = Fraction(e)
    return base ** int(e) if e.denominator == 1 else real_pow(base, e)


def solve(text: str, q: dict) -> dict:
    p = grab(r"USD {N} is compounded semiannually", text)
    y1 = grab(r"first {N} years?", text)
    r1 = grab(r"first [^;]*?nominal annual rate is {N} percent", text)
    y2 = grab(r"next {N} years?", text)
    r2 = grab(r"next {N} years? it is {N} percent", text, group=2)
    f1 = _pow(1 + r1 / 100 / 2, 2 * y1)
    f2 = _pow(1 + r2 / 100 / 2, 2 * y2)
    end = p * f1 * f2
    return {
        "final": end - p,
        "slots": {"first_growth_trace": f1, "second_growth_trace": f2, "ending_balance_trace": end},
    }
