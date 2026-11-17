from fractions import Fraction
import re

from finreason.nums import grab, real_pow

TEMPLATE_ID = "fp.investment_analysis.ci.quarterly_compound_interest.basic.v1"


def _pow(base: Fraction, n: Fraction) -> Fraction:
    if n.denominator == 1:
        return base ** int(n)
    return real_pow(base, n)


def solve(text: str, q: dict) -> dict:
    principal = grab(r"starts with\s+USD\s+{N}", text)
    rate = grab(r"nominal annual rate of\s+{N}\s+percent", text) / 100
    years = grab(r"compounds\s+\w+\s+for\s+{N}\s+years?", text)
    if re.search(r"\bm\s*=\s*-?\d", text):
        m = grab(r"\bm\s*=\s*{N}", text)
    else:
        m = Fraction(4)
    per = rate / m
    ending = principal * _pow(1 + per, m * years)
    return {
        "final": ending - principal,
        "slots": {
            "quarterly_rate_trace": per,
            "ending_balance_trace": ending,
        },
    }
