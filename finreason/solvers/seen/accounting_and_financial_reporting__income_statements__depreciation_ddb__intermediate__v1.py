from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.income_statements.depreciation_ddb.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"purchases an asset for {N} USD", text)
    life = grab(r"useful life of {N} years", text)
    # "exact annual rate 2 divided by useful life"
    try:
        mult = grab(r"exact annual rate {N} divided by useful life", text)
    except ValueError:
        mult = Fraction(2)
    rate = mult / life
    dep1 = cost * rate
    bv1 = cost - dep1
    dep2 = bv1 * rate
    bv2 = bv1 - dep2
    return {
        "final": bv2,
        "slots": {
            "ddb_rate_trace": rate,
            "year1_book_value_trace": bv1,
            "year2_depreciation_trace": dep2,
        },
    }
