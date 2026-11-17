import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.depreciation_and_amortization.sum_of_years_digits.basic.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"costs {N} USD", text)
    if re.search(r"\bzero residual value", text):
        residual = Fraction(0)
    else:
        residual = grab(r"residual value of {N} USD", text)
    n = grab(r"useful life of {N} years?", text)
    k = grab(r"depreciation in year {N}", text)
    syd = n * (n + 1) / 2
    remaining = n - k + 1
    if remaining < 0:  # beyond useful life: no depreciation
        remaining = Fraction(0)
    factor = remaining / syd
    dep = (cost - residual) * factor
    return {"final": dep, "slots": {"trace_1": syd, "trace_2": factor}}
