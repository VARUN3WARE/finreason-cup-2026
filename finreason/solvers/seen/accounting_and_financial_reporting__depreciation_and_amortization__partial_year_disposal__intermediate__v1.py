import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.depreciation_and_amortization.partial_year_disposal.intermediate.v1"


def _residual(text: str) -> Fraction:
    if re.search(r"\b(?:zero|no) (?:estimated )?(?:residual|salvage) value", text):
        return Fraction(0)
    return grab(r"(?:residual|salvage) value of (?:USD )?{N}", text)


def solve(text: str, q: dict) -> dict:
    cost = grab(r"costs (?:USD )?{N}", text)
    residual = _residual(text)
    life = grab(r"useful life of {N} years?", text)
    months = grab(r"receives {N} months? of straight-line depreciation", text)
    full_years = grab(r"then {N} complete depreciation years?", text)
    price = grab(r"sold immediately after those periods for (?:USD )?{N}", text)
    base = cost - residual
    annual = base / life  # trace_1
    # Straight-line accumulation stops once the depreciable base is exhausted.
    total_dep = min(annual * (months / 12 + full_years), base)  # trace_2
    carrying = cost - total_dep  # trace_3
    return {
        "final": price - carrying,
        "slots": {"trace_1": annual, "trace_2": total_dep, "trace_3": carrying},
    }
