from fractions import Fraction
import re
from finreason.nums import grab, F

TEMPLATE_ID = "fp.accounting_and_financial_reporting.income_statements.depreciation_ddb.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"purchases an asset for {N}\s*USD", text)
    life = grab(r"useful life of {N} years", text)
    # Residual value: stated as "zero" in the template; accept a number if given.
    salvage = Fraction(0)
    m = re.search(r"residual value is (-?\d[\d,]*(?:\.\d+)?)", text)
    if m:
        salvage = F(m.group(1))
    rate = Fraction(2) / life
    dep1 = cost * rate
    if cost - dep1 < salvage:
        dep1 = max(cost - salvage, Fraction(0))
    bv1 = cost - dep1
    dep2 = bv1 * rate
    if bv1 - dep2 < salvage:
        dep2 = max(bv1 - salvage, Fraction(0))
    bv2 = bv1 - dep2
    return {
        "final": bv2,
        "slots": {
            "ddb_rate_trace": rate,
            "year1_book_value_trace": bv1,
            "year2_depreciation_trace": dep2,
        },
    }
