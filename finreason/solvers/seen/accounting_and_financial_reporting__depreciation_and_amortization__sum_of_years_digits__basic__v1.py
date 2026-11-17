import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.depreciation_and_amortization.sum_of_years_digits.basic.v1"


def _residual(text: str) -> Fraction:
    if re.search(r"\b(?:zero|no) (?:estimated )?(?:residual|salvage) value", text):
        return Fraction(0)
    return grab(r"(?:residual|salvage) value of (?:USD )?{N}", text)


def solve(text: str, q: dict) -> dict:
    cost = grab(r"costs (?:USD )?{N}", text)
    residual = _residual(text)
    life = grab(r"useful life of {N} years?", text)
    year = grab(r"depreciation in year {N}", text)
    n = int(life)
    syd = Fraction(n * (n + 1), 2)  # trace_1: 1 + 2 + ... + n
    # Remaining life at the start of the requested year; years outside the useful life
    # (before year 1 or after year n) carry no depreciation.
    remaining = life - year + 1
    if year < 1 or remaining <= 0:
        remaining = Fraction(0)
    factor = remaining / syd  # trace_2
    return {"final": (cost - residual) * factor, "slots": {"trace_1": syd, "trace_2": factor}}
