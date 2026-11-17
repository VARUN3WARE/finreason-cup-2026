import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.depreciation_and_amortization.straight_line_depreciation.basic.v1"


def _residual(text: str) -> Fraction:
    if re.search(r"\b(?:zero|no) (?:estimated )?(?:residual|salvage) value", text):
        return Fraction(0)
    return grab(r"(?:residual|salvage) value of (?:USD )?{N}", text)


def solve(text: str, q: dict) -> dict:
    cost = grab(r"costs (?:USD )?{N}", text)
    residual = _residual(text)
    life = grab(r"useful life of {N} years?", text)
    base = cost - residual  # depreciable base (trace_1)
    return {"final": base / life, "slots": {"trace_1": base}}
