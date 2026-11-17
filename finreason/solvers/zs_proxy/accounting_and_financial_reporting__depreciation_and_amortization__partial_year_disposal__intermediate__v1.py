import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.depreciation_and_amortization.partial_year_disposal.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"costs {N} USD", text)
    if re.search(r"\bzero residual value", text):
        residual = Fraction(0)
    else:
        residual = grab(r"residual value of {N} USD", text)
    life = grab(r"useful life of {N} years?", text)
    months = grab(r"receives {N} months? of straight-line depreciation", text)
    years = grab(r"then {N} complete depreciation years?", text)
    sale = grab(r"sold immediately after those periods for {N} USD", text)

    depreciable = cost - residual
    annual = depreciable / life
    total = annual * (months / 12 + years)
    # Cannot depreciate below residual value (standard cap; not reached when periods <= life).
    total = min(total, depreciable)
    carrying = cost - total
    gain = sale - carrying
    return {"final": gain, "slots": {"trace_1": annual, "trace_2": total, "trace_3": carrying}}
