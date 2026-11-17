import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.depreciation_and_amortization.straight_line_depreciation.basic.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"costs {N} USD", text)
    if re.search(r"\bzero residual value", text):
        residual = Fraction(0)
    else:
        residual = grab(r"residual value of {N} USD", text)
    life = grab(r"useful life of {N} years?", text)
    depreciable = cost - residual
    return {"final": depreciable / life, "slots": {"trace_1": depreciable}}
